import pandas as pd
import logging
from app.utils.fileHandler import load_file
from app.models.common.fileStore import FilePaths

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 자재와 수요 데이터 로드
def process_material_data():
    material_file_path = FilePaths.get("dynamic_excel_file")

    if material_file_path:
        df_material = load_file(material_file_path)
        df_material_qty = df_material.get('material_qty', pd.DataFrame())
        logger.info(f"로드된 자재 수량 데이터 형태: {df_material_qty.shape}")

        if df_material_qty.empty:
            return None
        
        processed_data = preprocess_material_data(df_material_qty)
        logger.info(f"처리된 자재 데이터 컬럼: {list(processed_data['material_df'].columns)}")
        logger.info(f"처리된 날짜 컬럼: {processed_data['date_columns']}")
        return processed_data
    else:
        return None

# 자재 만족률 분석을 위한 데이터 처리
def process_material_satisfaction_data() :
    dynamic_file_path = FilePaths.get('dynamic_excel_file')
    demand_file_path = FilePaths.get('demand_excel_file')

    if not dynamic_file_path :
        return {'dynamic 파일을 불러오지 못했습니다'}

    if not demand_file_path :
        return {'demand 파일을 불러오지 못했습니다'}
    
    try :
        df_dynamic = load_file(dynamic_file_path)
        df_demand = load_file(demand_file_path)
        df_material_qty = df_dynamic.get('material_qty', pd.DataFrame())
        df_material_item = df_dynamic.get('material_item', pd.DataFrame())
        df_demand_data = df_demand.get('demand', pd.DataFrame())

        if df_demand_data.empty :
            return {'error' : 'demand 데이터를 찾을 수 없습니다'}
        
        if 'SOP' in df_demand_data.columns :
            df_demand_data['SOP'] = df_demand_data['SOP'].apply(
                lambda x : max(0, float(x)) if pd.notnull(x) else 0
            )

        if df_material_qty.empty :
            return None
        
        if df_material_item.empty :
            return None
        
        material_data = preprocess_material_data(df_material_qty)
        material_df = material_data['material_df']
        material_item_df = df_material_item.copy()
        material_equal_df = df_dynamic.get('material_equal', pd.DataFrame())

        logger.info(f"처리된 자재 데이터 형태: {material_df.shape}")
        logger.info(f"날짜 컬럼 목록: {material_data['date_columns']}")
        logger.info(f"주간 컬럼 목록: {material_data['weekly_columns']}")

        # On-Hand 컬럼 샘플 값 확인
        if 'On-Hand' in material_df.columns:
            logger.info(f"On-Hand 컬럼 통계: 최소={material_df['On-Hand'].min()}, 최대={material_df['On-Hand'].max()}, 평균={material_df['On-Hand'].mean()}")
            # 음수 값 확인
            negative_count = (material_df['On-Hand'] < 0).sum()
            logger.info(f"On-Hand 컬럼 음수 값 개수: {negative_count}")
            if negative_count > 0:
                sample_negatives = material_df[material_df['On-Hand'] < 0].head(5)
                logger.info(f"음수 On-Hand 값 샘플:\n{sample_negatives[['Material', 'On-Hand']]}")
        
        # 날짜별 수량 샘플 확인
        if material_data['date_columns']:
            first_date_col = material_data['date_columns'][0]
            non_zero_count = (material_df[first_date_col] != 0).sum()
            logger.info(f"{first_date_col} 컬럼 비-0 값 개수: {non_zero_count}")
            if non_zero_count > 0:
                sample_non_zero = material_df[material_df[first_date_col] != 0].head(5)
                logger.info(f"비-0 {first_date_col} 값 샘플:\n{sample_non_zero[['Material', first_date_col]]}")


        return {
            'material_df' : material_df,
            'material_item_df' : material_item_df,
            'material_equal_df' : material_equal_df if not material_equal_df.empty else None,
            'demand_df' : df_demand_data,
            'date_columns' : material_data['date_columns'],
            'weekly_columns' : material_data['weekly_columns']
        }

    except Exception as e :
        return {'error' : f'데이터 로드와 전처리 중 오류 발생 : {str(e)}'}
    
    
# 자재 데이터 전처리 후 변환
def preprocess_material_data(df_material_qty) :

    if 'Active_OX' not in df_material_qty.columns and isinstance(df_material_qty.iloc[0, 0], str) :
        column_names = df_material_qty.iloc[0].tolist()
        df_material_qty = df_material_qty.iloc[1:].reset_index(drop=True)
        df_material_qty.columns = column_names

    required_columns = ['Active_OX', 'Material', 'On-Hand']

    all_columns = list(df_material_qty.columns)

    if 'On-Hand' in all_columns :
        on_hand_index = all_columns.index('On-Hand')
        date_columns = all_columns[on_hand_index + 1:]
    else :
        date_columns = []
    
    required_columns.extend(date_columns)

    existing_columns = [col for col in required_columns if col in df_material_qty.columns]
    df_filtered = df_material_qty[existing_columns].copy()

    numeric_columns = ['On-Hand'] + date_columns

    for col in numeric_columns :
        if col in df_filtered.columns :
            df_filtered[col] = df_filtered[col].apply(lambda x : convert_to_numeric(x))

    weekly_columns = date_columns

    processed_data = {
        'material_df' : df_filtered,
        'date_columns' : date_columns,
        'weekly_columns' : weekly_columns
    }

    return processed_data

# 값을 숫자로 변환하는 함수
def convert_to_numeric(value) :
    if pd.isna(value) or value == '' :
        return 0
    
    if isinstance(value, str) :
        value = value.replace(',', '')

        try :
            return float(value)
        except ValueError :
            return 0
        
    return float(value) if value else 0
