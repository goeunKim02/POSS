import pandas as pd
import numpy as np
from typing import List, Tuple
from app.models.input.maintenance import ItemMaintenance, RMCMaintenance, DataLoader

def melt_plan(df: pd.DataFrame) -> pd.DataFrame:
    records = []
    for _, row in df.iterrows():
        for day in range(1, 8):
            item = row[f'Item{day}']
            qty = row[f'Qty{day}']
            if pd.notna(item) and qty > 0:
                real_shift = (day - 1) * 2 + row['Shift']
                records.append({
                    'Line':  row['Line'],
                    'Shift': real_shift,
                    'Item':  item,
                    'Qty':   qty
                })
    return pd.DataFrame(records)

def get_threshold(shift: int, mode: str) -> float:
    if shift in (1,2):
        return 0.90 if mode=='item' else 0.95
    if shift in (3,4):
        return 0.80 if mode=='item' else 0.90
    return np.nan

def analyze_maintenance(
    prev_df: pd.DataFrame,
    new_df:  pd.DataFrame
) -> Tuple[List[ItemMaintenance], List[RMCMaintenance]]:

    df_prev = melt_plan(prev_df).rename(columns={'Qty':'prev_qty'})
    df_new = melt_plan(new_df) .rename(columns={'Qty':'new_qty'})
    print(df_new)
    print(df_prev)
    df = (
        pd.merge(df_prev, df_new,
                 on=['Line','Shift','Item'],
                 how='outer')
          .fillna(0)
    )
    df['maintain_qty'] = df[['prev_qty','new_qty']].min(axis=1)
    df['RMC'] = df['Item'].str[3:-7]

    items = []
    for (line, shift, item), g in df.groupby(['Line','Shift','Item'], sort=False):
        prev_qty = g['prev_qty'].sum()
        new_qty = g['new_qty'].sum()
        m_qty = g['maintain_qty'].sum()
        m_rate = (m_qty/prev_qty) if prev_qty>0 else None
        thresh = get_threshold(shift, 'item')
        below = (m_rate is not None and m_rate < thresh)
        items.append(ItemMaintenance(
            line, shift, item,
            prev_qty, new_qty, m_qty,
            m_rate, thresh, below
        ))

    rmcs = []
    for (line, shift, rmc), g in df.groupby(['Line','Shift','RMC'], sort=False):
        prev_qty = g['prev_qty'].sum()
        new_qty = g['new_qty'].sum()
        m_qty = g['maintain_qty'].sum()
        m_rate = (m_qty/prev_qty) if prev_qty>0 else None
        thresh = get_threshold(shift, 'rmc')
        below = (m_rate is not None and m_rate < thresh)
        rmcs.append(RMCMaintenance(
            line, shift, rmc,
            prev_qty, new_qty, m_qty,
            m_rate, thresh, below
        ))

    return items, rmcs

def run_maintenance_analysis() -> Tuple[List[ItemMaintenance], List[RMCMaintenance]]:
    prev_df = DataLoader.load_dynamic_data()
    print(prev_df.columns.tolist())
    new_df = DataLoader.load_pre_assign_data()
    print(new_df.columns.tolist())

    items, rmcs = analyze_maintenance(prev_df, new_df)

    failed_items = [i for i in items if i.below_thresh]
    failed_rmcs = [r for r in rmcs  if r.below_thresh]

    return failed_items, failed_rmcs