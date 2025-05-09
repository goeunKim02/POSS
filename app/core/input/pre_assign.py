import fnmatch
from collections import defaultdict
from typing import Tuple

import pandas as pd

from ...models.input.pre_assign import Request, PreAssignSolution, PreAssignFailures, DataLoader

"""dynamic, demand, master 데이터를 로드"""
def load_data():
    # dynamic 데이터
    try:
        fixed_opt, pre_assign = DataLoader.load_dynamic_data()
    except Exception as e:
        print(f"[load_data] load_dynamic_data 에러: {e}")
        fixed_opt, pre_assign = pd.DataFrame(), pd.DataFrame()

    # demand 데이터
    try:
        demand = DataLoader.load_demand_data()
    except Exception as e:
        print(f"[load_data] load_demand_data 에러: {e}")
        demand = pd.DataFrame(columns=['Item', 'MFG'])

    # master 데이터
    try:
        line_avail, capa_qty = DataLoader.load_master_data()
    except Exception as e:
        print(f"[load_data] load_master_data 에러: {e}")
        line_avail, capa_qty = pd.DataFrame(), pd.DataFrame()

    if not capa_qty.empty and 'Line' in capa_qty.columns:
        capa_qty = capa_qty.set_index('Line')
    else:
        capa_qty = pd.DataFrame()

    return fixed_opt, pre_assign, demand, line_avail, capa_qty

def expand_pre_assign(fixed_opt: pd.DataFrame, pre_assign: pd.DataFrame) -> pd.DataFrame:
    """fixed_option 확장(pre_assign > fixed_option)"""
    records = []
    for _, row in pre_assign.iterrows():
        shift = row['Shift']
        for k in range(1, 8):
            item, qty = row[f'Item{k}'], row[f'Qty{k}']
            if pd.notna(item) and pd.notna(qty):
                t = (k - 1) * 2 + shift
                records.append({
                    'Fixed_Group': item,
                    'Fixed_Line' : row['Line'],
                    'Fixed_Time' : t,
                    'Qty'        : qty
                })
    return pd.concat([fixed_opt, pd.DataFrame(records)], ignore_index=True, sort=False)

def process_all_qty(fixed_opt: pd.DataFrame, demand: pd.DataFrame) -> pd.DataFrame:
    """Qty == 'ALL'일 때 demand 합계로 대체"""
    def resolve_qty(row):
        q = row['Qty']
        if q == 'ALL':
            pat = row['Fixed_Group'].replace('*','?')
            return demand.loc[
                demand['Item'].apply(lambda s: fnmatch.fnmatch(s, pat)),
                'MFG'
            ].sum()
        return q

    fixed_opt['Qty'] = fixed_opt.apply(resolve_qty, axis=1)
    return fixed_opt.dropna(subset=['Qty']).copy()

"""Fixed_Line 검증 & 정리"""
def validate_fixed_lines(
    fixed_opt: pd.DataFrame,
    line_avail: pd.DataFrame
) -> pd.DataFrame:
    drops = []
    for idx, row in fixed_opt.iterrows():
        proj_code = row['Fixed_Group'][3:7]
        raw_line  = str(row.get('Fixed_Line', '')).strip()

        # 해당 프로젝트를 포함하는 행 검색
        avail_df = line_avail[line_avail['Project'].str.contains(proj_code, na=False)]
        if avail_df.empty:
            drops.append(idx)
            continue

        avail = avail_df.iloc[0]

        # Fixed_Line이 비어있거나 'nan'인 경우, 상태가 1인 모든 라인 선택
        if not raw_line or raw_line.lower() == 'nan':
            lines = [ln for ln, v in avail.drop('Project').items() if v == 1]
        else:
            lines = [ln.strip() for ln in raw_line.split(',') if ln.strip()]

        # 허용되지 않는 라인 검사
        invalid = [ln for ln in lines if avail.get(ln, 0) != 1]
        if invalid:
            drops.append(idx)
        else:
            fixed_opt.at[idx, 'Fixed_Line'] = ','.join(lines)

    return fixed_opt.drop(index=drops).reset_index(drop=True)

def validate_capacity_and_time(fixed_opt: pd.DataFrame, capa_qty: pd.DataFrame) -> pd.DataFrame:
    """용량 검증 & Fixed_Time 정리"""
    drops = []
    all_times = [int(t) for t in capa_qty.columns]
    for idx, row in fixed_opt.iterrows():
        lines = row['Fixed_Line'].split(',')
        rawt  = str(row['Fixed_Time'])
        times = all_times if not rawt or rawt.lower()=='nan' else [int(t) for t in rawt.split(',')]
        total_cap = sum(capa_qty.at[l,t] for l in lines for t in times)
        if float(row['Qty']) > total_cap:
            drops.append(idx)
        else:
            fixed_opt.at[idx,'Fixed_Time'] = ','.join(map(str,times))
    return fixed_opt.drop(index=drops)

def parse_group_constraints(capa_qty: pd.DataFrame):
    """그룹별 제약 파싱"""
    max_line, max_qty = {}, {}
    for row_idx in capa_qty.index:
        if isinstance(row_idx, str) and row_idx.startswith('Max_line_'):
            grp = row_idx.split('_')[-1]
            max_line[grp] = {int(t): int(v) for t,v in capa_qty.loc[row_idx].items() if pd.notna(v)}
        if isinstance(row_idx, str) and row_idx.startswith('Max_qty_'):
            grp = row_idx.split('_')[-1]
            max_qty[grp]  = {int(t): float(v) for t,v in capa_qty.loc[row_idx].items() if pd.notna(v)}
    return max_line, max_qty

def build_requests(fixed_opt: pd.DataFrame) -> list[Request]:
    """요청 리스트 생성"""
    requests = []
    for idx, row in fixed_opt.iterrows():
        req = Request(
            idx=idx,
            lines=row['Fixed_Line'].split(','),
            times=[int(t) for t in row['Fixed_Time'].split(',')],
            qty=float(row['Qty'])
        )
        requests.append(req)
    return requests

def init_capacity(capa_qty: pd.DataFrame):
    """초기 용량 할당 상태 생성"""
    cap = {(l, int(t)): capa_qty.at[l,t] for l in capa_qty.index if not str(l).startswith('Max_') for t in capa_qty.columns}
    return cap, defaultdict(int), defaultdict(float)

def allocate_split(req: Request, cap: dict, used_l: dict, used_q: dict,
                   max_line: dict, max_qty: dict,
                   solution: PreAssignSolution) -> Tuple[bool, list[dict]]:
    """
    분할할당 함수
    Returns:
      ok: bool
      failures: list of {
          "line": str,        # ex. "I_04-10"
          "reason": str,      # ex. "qty 한도"
          "available": float, # 현재 cap[(l,t)]
          "excess": float     # 남은 q_rem
      }
    """
    q_rem = req.qty
    failures = []

    for l in req.lines:
        for t in req.times:
            avail = cap[(l, t)]
            grp   = l.split('_')[0]

            # qty 제한
            print(avail)
            if avail <= 0:
                failures.append({
                    "line":      f"{l}-{t}",
                    "reason":    "qty 제한",
                    "available": avail,
                    "excess":    q_rem
                })
                continue

            # max_line 제한
            if t in max_line.get(grp, {}) and used_l[(grp, t)] >= max_line[grp][t]:
                failures.append({
                    "line":      f"{l}-{t}",
                    "reason":    "max_line 제한",
                    "available": avail,
                    "excess":    q_rem
                })
                continue

            # max_qty 한도
            if t in max_qty.get(grp, {}) and used_q[(grp, t)] >= max_qty[grp][t]:
                failures.append({
                    "line":      f"{l}-{t}",
                    "reason":    "max_qty 제한",
                    "available": avail,
                    "excess":    q_rem
                })
                return False, failures

            # 실제 할당 가능한 최대량 계산
            cap_lim = avail
            qty_lim = (max_qty[grp][t] - used_q[(grp, t)]) if t in max_qty.get(grp, {}) else float('inf')
            alloc   = min(q_rem, cap_lim, qty_lim)

            if alloc <= 0:
                failures.append({
                    "line":      f"{l}-{t}",
                    "reason":    "할당 가능량 0",
                    "available": cap_lim,
                    "excess":    q_rem
                })
                continue

            # 실제 할당
            cap[(l, t)]      -= alloc
            used_l[(grp, t)] += 1
            used_q[(grp, t)] += alloc
            solution.setdefault(req.idx, []).append((l, t, alloc))
            q_rem -= alloc

            # 전부 할당되면 성공 리턴
            if q_rem <= 0:
                return True, []

    # 남은 물량이 있으면 TOTAL 항목으로 기록
    if q_rem > 0:
        failures.append({
            "line":      f"{l}-{t}",
            "reason":    "qty 제한",
            "available": None,
            "excess":    q_rem
        })

    return False, failures

def run_allocation() -> Tuple[PreAssignSolution, PreAssignFailures]:
    """전체 할당 실행"""
    fx, pa, dm, la, cq = load_data()
    fx = expand_pre_assign(fx, pa)
    fx = process_all_qty(fx, dm)
    fx = validate_fixed_lines(fx, la)
    fx = validate_capacity_and_time(fx, cq)

    max_ln, max_q = parse_group_constraints(cq)
    requests = build_requests(fx)
    cap, used_l, used_q = init_capacity(cq)

    solution = {}
    failures = {}

    all_errors = []
    for req in requests:
        ok, errs = allocate_split(req, cap, used_l, used_q, max_ln, max_q, solution)
        if not ok:
            all_errors.extend(errs)

    failures["preassign"] = all_errors

    return solution, failures