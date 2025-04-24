import pandas as pd

class PreAssignment:
    df_demand = pd.read_excel('ssafy_demand_0408.xlsx', sheet_name="demand")
    for i, row in df_demand.iterrows() :    
        df_demand.loc[i, "Project"] = row["Item"][3:7]
        df_demand.loc[i, "Basic2"] = row['Item'][3:8]
        df_demand.loc[i, "Tosite_group"] = row["Item"][7:8]
        df_demand.loc[i, "RMC"] = row['Item'][3:-3]
        df_demand.loc[i, "Color"] = row['Item'][8:-4]
    item = df_demand.index.tolist()
    project = df_demand["Basic2"].unique()
    RMC = df_demand.RMC.unique()

    df_capa_portion = pd.read_excel('ssafy_master_0408.xlsx',sheet_name='capa_portion')
    df_capa_qty = pd.read_excel('ssafy_master_0408.xlsx', sheet_name="capa_qty")
    df_line_available = pd.read_excel('ssafy_master_0408.xlsx', sheet_name="line_available")
    df_capa_outgoing = pd.read_excel('ssafy_master_0408.xlsx',sheet_name="capa_outgoing")
    df_capa_imprinter = pd.read_excel('ssafy_master_0408.xlsx',sheet_name="capa_imprinter")
    df_due_LT = pd.read_excel('ssafy_master_0408.xlsx',sheet_name="due_LT")
    time = {i for i in df_capa_qty.columns}
    line = df_line_available.columns
    port_list = df_capa_outgoing.Tosite_port.unique()
    day_list = list(reversed(range(1, 8)))

    df_material_item = pd.read_excel('ssafy_dynamic_0408.xlsx',sheet_name='material_item')
    df_material_qty = pd.read_excel('ssafy_dynamic_0408.xlsx',sheet_name='material_qty')
    df_material_equal = pd.read_excel('ssafy_dynamic_0408.xlsx',sheet_name='material_equal')
    df_due_request = pd.read_excel('ssafy_dynamic_0408.xlsx',sheet_name='due_request')
    df_pre_assign = pd.read_excel('ssafy_dynamic_0408.xlsx',sheet_name='pre_assign')
    df_fixed_option = pd.read_excel('ssafy_dynamic_0408.xlsx',sheet_name='fixed_option')

    def execute(self):
        print("run execute")


if __name__ == "__main__":
    pre_assignment = PreAssignment()
    pre_assignment.execute()
