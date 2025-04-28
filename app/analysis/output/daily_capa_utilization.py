import pandas as pd
import numpy as np

def analyze_utilization(file_path, qty_file_path):
    # Load demand data from Excel
    df_demand = pd.read_excel(file_path)

    # Load capacity quantity data from Excel
    df_capa_qty = pd.read_excel(qty_file_path, sheet_name="capa_qty")

    # Map shifts to days of week
    shift_to_day = {
        1: 'Mon', 2: 'Mon',
        3: 'Tue', 4: 'Tue',
        5: 'Wed', 6: 'Wed',
        7: 'Thu', 8: 'Thu',
        9: 'Fri', 10: 'Fri',
        11: 'Sat', 12: 'Sat',
        13: 'Sun', 14: 'Sun',
    }

    # Calculate daily capacity 
    day_capacity = {}
    for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
        day_shifts = [shift for shift, d in shift_to_day.items() if d == day]
        day_total_capacity = 0

        for shift in day_shifts:
            shift_capacity = 0

            # Process each manufacturing building
            for factory in ['I', 'D', 'K', 'M']:
                # Get lines for this factory
                factory_lines = df_capa_qty[df_capa_qty['Line'].str.startswith(f'{factory}_')].index.tolist()
               
                if not factory_lines or shift not in df_capa_qty.columns:
                    continue

                # Check max_line constraint
                max_line_key = f'Max_line_{factory}'
                # if no constraint, use total number of lines
                max_line = df_capa_qty.loc[max_line_key, shift] if max_line_key in df_capa_qty.index and pd.notna(df_capa_qty.loc[max_line_key, shift]) else len(factory_lines)

                # Get production capacity for each line
                line_capacities = [(line, df_capa_qty.loc[line, shift]) for line in factory_lines if pd.notna(df_capa_qty.loc[line, shift])]
                line_capacities.sort(key=lambda x:x[1], reverse=True)  # Sort by capacity in descending order
                
                # Check max_qty constraint
                max_qty_key = f'Max_qty_{factory}'
                max_qty = df_capa_qty.loc[max_qty_key, shift] if max_qty_key in df_capa_qty.index and pd.notna(df_capa_qty.loc[max_qty_key, shift]) else float('inf')

                # Apply the more restrictive constraints between line count and max qty
                factory_capacity = 0
                for i, (line, capacity) in enumerate(line_capacities):
                    if i < max_line and factory_capacity + capacity <= max_qty:
                        factory_capacity += capacity
                    elif i < max_line and factory_capacity < max_qty:
                        factory_capacity = max_qty # Max qty constraint reached
                        break
                
                shift_capacity += factory_capacity

            day_total_capacity += shift_capacity
        
        day_capacity[day] = day_total_capacity
    
    # Calculate daily production based on demand qty
    df_demand['Day'] = df_demand['Time'].map(shift_to_day)
    day_production = df_demand.groupby('Day')['Qty'].sum()

    # Calculate utilization rate by day
    utilization_rate = {}
    for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
        if day in day_capacity and day_capacity[day] > 0:
            if day in day_production:
                utilization_rate[day] = (day_production[day] / day_capacity[day]) * 100
            else:
                utilization_rate[day] = 0
        else:
            utilization_rate[day] = 0 if day_capacity[day] == 0 else None

    print("daily utilization rate(%):")
    for day, rate in utilization_rate.items():
        if rate is not None:
            print(f"{day}: {rate:.2f}%")
        else:
            print(f"{day}: No capacity availble")

    return utilization_rate

if __name__ == "__main__":
    file_path = "app/analysis/output/ssafy_result_0408.xlsx"
    qty_file_path = "app/analysis/output/ssafy_master_0408.xlsx"
    utilization_df = analyze_utilization(file_path, qty_file_path)
