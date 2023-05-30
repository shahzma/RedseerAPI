# %%
from sqlalchemy.orm import sessionmaker, Session
import pandas as pd
from datetime import datetime, date, timedelta
import openpyxl
import calendar, math

from FormAPI.utils.ReportAnalysis.common_func import par_val_df, InsertORUpdate, get_db_connection
from django.conf import settings

db_settings = settings.DATABASES['default']

def month_range(sd):
    Total_number_days=calendar.monthrange(sd.year, sd.month)[1]
    return Total_number_days

def end_date(sd):
    year = sd.year
    month = sd.month
    return date(year, month, calendar.monthrange(year, month)[1])

# %%
def Citywise_agg(player_id, Metric, db_conn, db_session):
    Citywise_mapping = pd.read_excel("Mobility_sector_total.xlsx", sheet_name = Metric)
    required_par = Citywise_mapping["Cab_id"].dropna().to_list()
    required_par.extend(Citywise_mapping["Auto_id"].dropna().to_list())
    required_par.extend(Citywise_mapping["Moto_id"].dropna().to_list())
    citywise_data = pd.read_sql(f"select start_date, parameter_id, value from main_data where player_id = {player_id} and parameter_id in {tuple(required_par)};", db_conn)
    citywise_data["start_date"] = pd.to_datetime(citywise_data["start_date"]).dt.date
    transformed_df = citywise_data.pivot_table(index= "start_date", columns= "parameter_id", values= "value")
    
    output_df = pd.DataFrame(index= transformed_df.index)
    Start_date = pd.Series(output_df.index.values).apply(str)
    End_date = pd.Series(output_df.index.values).apply(end_date).apply(str)
    mapping_dict = Citywise_mapping.drop("City", axis = 1).set_index("parameter_id")[["Cab_id", "Auto_id", "Moto_id"]].to_dict(orient = "index")
    mapping_dict = {key: list(edit_dict.values()) for key, edit_dict in mapping_dict.items()}
    for key, sum_params in mapping_dict.items():
        sum_params = [int(x) for x in sum_params if not math.isnan(x)]
        try:
            output_df[int(key)] = transformed_df[sum_params].sum(axis = 1)
        except KeyError as e:
            print("KeyError", e.args[0])

    commom_params = [player_id, str(date.today()), 'webforms_calc', 52]
    required_df = pd.DataFrame(columns= ['start_date', 'end_date', 'parameter_id', 'value'])
    for par_id in output_df.columns.values:
        # print(par_id)
        new_df = pd.DataFrame()
        new_df['start_date'] = Start_date
        new_df['end_date'] = End_date
        new_df['parameter_id'] = par_id
        new_df['value'] = pd.Series(output_df[par_id].values)
        # print(new_df['value'])
        required_df = pd.concat([required_df, new_df], axis= 0)

    required_df[['player_id', 'date_created', 'source', 'parametertree_id']] = commom_params
    required_df = required_df.reindex(columns= ['player_id', 'start_date', 'end_date', 'parameter_id', 'value', 'date_created', 'source', 'parametertree_id'])
    required_df.dropna(subset = ['value'], inplace = True)
    required_df = required_df.loc[~(required_df["value"] == 0)]
    data_tuples = [tuple(x) for x in required_df.to_records(index= False)]
    InsertORUpdate(data_tuples, db_conn, db_session)

# %%
def Mobility_aggregate(sector_tot_id, db_conn, db_session):
    players = [156, 157, 158]
    workbook = openpyxl.load_workbook("Mobility_sector_total.xlsx")
    sheets = workbook.worksheets
    print(sheets)
    for sheet in sheets:
        for player_id in players:
            Citywise_agg(player_id, sheet.title, db_conn, db_session)
            
    input_df = par_val_df(players, db_conn)
    output_df = pd.DataFrame(index=input_df.index.get_level_values(0).drop_duplicates())
    Start_date = pd.Series(output_df.index.values).apply(str)
    End_date = pd.Series(output_df.index.values).apply(end_date).apply(str)

    #Gross Booking value
    output_df[2115] = input_df[2115].groupby(level= 0).sum()
    output_df[2214] = input_df[2214].groupby(level = 0).sum()
    output_df[2116] = input_df[2116].groupby(level = 0).sum()
    output_df[2228] = input_df[2228].groupby(level = 0).sum()

    # Bookings
    output_df[1971] = input_df[1971].groupby(level = 0).sum()    
    output_df[1972] = input_df[1972].groupby(level = 0).sum()    
    output_df[2070] = input_df[2070].groupby(level = 0).sum()    
    output_df[2084] = input_df[2084].groupby(level = 0).sum()    

    # Average ride value 
    output_df[2259] = input_df[2115].groupby(level = 0).sum()/input_df[1971].groupby(level= 0).sum()
    output_df[2260] = input_df[2116].groupby(level = 0).sum()/input_df[1972].groupby(level= 0).sum()
    output_df[2358] = input_df[2214].groupby(level = 0).sum()/input_df[2070].groupby(level= 0).sum()
    output_df[2372] = input_df[2228].groupby(level = 0).sum()/input_df[2084].groupby(level= 0).sum()

    # Citywise Gross Booking Value & Bookings
    for sheet in sheets:
        mapping_df = pd.read_excel("Mobility_sector_total.xlsx", sheet_name= sheet.title)
        Metric_ids = mapping_df["parameter_id"]    
        for par_id in Metric_ids:
            try:
                output_df[par_id] = input_df[par_id].groupby(level = 0).sum()
            except KeyError as e:
                print("KeyError", e.args[0])

    commom_params = [sector_tot_id, str(date.today()), 'webforms_calc', 52]
    required_df = pd.DataFrame(columns= ['start_date', 'end_date', 'parameter_id', 'value'])
    for par_id in output_df.columns.values:
        # print(par_id)
        new_df = pd.DataFrame()
        new_df['start_date'] = Start_date
        new_df['end_date'] = End_date
        new_df['parameter_id'] = par_id
        new_df['value'] = pd.Series(output_df[par_id].values)
        # print(new_df['value'])
        required_df = pd.concat([required_df, new_df], axis= 0)

    required_df[['player_id', 'date_created', 'source', 'parametertree_id']] = commom_params
    required_df = required_df.reindex(columns= ['player_id', 'start_date', 'end_date', 'parameter_id', 'value', 'date_created', 'source', 'parametertree_id'])
    required_df.dropna(subset = ['value'], inplace = True)
    required_df = required_df.loc[~(required_df["value"] == 0)]
    data_tuples = [tuple(x) for x in required_df.to_records(index= False)]
    InsertORUpdate(data_tuples, db_conn, db_session)
    

# %%
# sector total player -> 336
if __name__ == "__main__":
    database_name = db_settings['NAME']
    db_session, db_conn = get_db_connection(database_name)
    Mobility_aggregate(336, db_conn, db_session)


