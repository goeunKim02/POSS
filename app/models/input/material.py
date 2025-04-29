import pandas as pd
from app.utils.fileHandler import load_file
from app.models.common.fileStore import FilePaths

def process_material_data() :
    material_file_path = FilePaths.get("dynamic_excel_file")

    if material_file_path :
        df_material = load_file(material_file_path)
        df_material_qty = df_material.get('material_qty', pd.DataFrame())

        if df_material_qty.empty :
            return None
        
        processed_data = preprocess_material_data(df_material_qty)
        return processed_data
    else :
        return None
    
# 자재 데이터 전처리 후 변환
def preprocess_material_data(df_material_qty) :

    if 'Active_OX' not in df_material_qty.columns and isinstance(df_material_qty.iloc[0, 0], str) :
        column_names = df_material_qty.iloc[0].tolist()
        df_material_qty = df_material_qty.iloc[1:].reset_index(drop=True)
        df_material_qty.columns = column_names

    required_columns = ['Active_OX', 'Material', 'On-Hand']

    date_columns = [f'4/{day}({get_day_of_week(day)})' for day in range(7, 21)]
    required_columns.extend(date_columns)

    existing_columns = [col for col in required_columns if col in df_material_qty.columns]
    df_filtered = df_material_qty[existing_columns].copy()

    numeric_columns = ['On-Hand'] + date_columns

    for col in numeric_columns :
        if col in df_filtered.columns :
            df_filtered[col] = df_filtered[col].apply(lambda x : convert_to_numeric(x))

    processed_data = {
        'material_df' : df_filtered,
        'date_columns' : [col for col in date_columns if col in df_filtered.columns],
        'weekly_columns' : [col for col in date_columns if col in df_filtered.columns and int(col.split('/')[1].split('(')[0]) <= 13]
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

# 요일 반환하는 함수
def get_day_of_week(day) :
    days_of_week = ['월', '화', '수', '목', '금', '토', '일']
    return days_of_week[(day - 7) % 7]