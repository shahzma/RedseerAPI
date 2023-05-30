# %%
from sqlalchemy.orm import sessionmaker, Session
import pandas as pd
from datetime import datetime, date, timedelta
import calendar

from FormAPI.utils.ReportAnalysis.common_func import par_val_df, InsertORUpdate, get_db_connection
from django.conf import settings

db_settings = settings.DATABASES['default']

# %%
def month_range(sd):
    Total_number_days=calendar.monthrange(sd.year, sd.month)[1]
    return Total_number_days

def end_date(sd):
    year = sd.year
    month = sd.month
    return date(year, month, calendar.monthrange(year, month)[1])


# %%
#sector agg functions
def CSM_agg(sector_tot_id, db_conn, db_session):
    players = [1, 4, 5, 10, 11, 12]
    input_df = par_val_df(players, db_conn)
    output_df = pd.DataFrame(index=input_df.index.get_level_values(0).drop_duplicates())
    Start_date = pd.Series(output_df.index.values).apply(str)
    End_date = pd.Series(output_df.index.values).apply(end_date).apply(str)

    output_df[128] = input_df[128].groupby(level= 0).sum()

    output_df[117] = input_df[117].groupby(level= 0).sum()
    output_df[118] = input_df[118].groupby(level= 0).sum()
    output_df[119] = input_df[119].groupby(level= 0).sum()
    output_df[43] = input_df[43].groupby(level= 0).sum()
    output_df[73] = input_df[73].groupby(level= 0).sum()
    output_df[104] = input_df[104].groupby(level= 0).sum()
    output_df[137] = input_df[137].groupby(level= 0).sum()
    output_df[138] = input_df[138].groupby(level= 0).sum()
    output_df[139] = input_df[139].groupby(level= 0).sum()
    output_df[140] = input_df[140].groupby(level= 0).sum()

    output_df[35] = input_df[35].groupby(level= 0).mean()
    output_df[24] = input_df[24].groupby(level= 0).mean()

    output_df[7] = input_df[7].groupby(level= 0).sum()
    output_df[12] = input_df[12].groupby(level= 0).sum()

    input_df[5125] = input_df[137]/input_df[57]
    input_df[5126] = input_df[138]/input_df[158]
    input_df[5127] = input_df[139]/input_df[159]
    input_df[5128] = input_df[140]/input_df[160]
    input_df[5129] = input_df[117]/input_df[59]
    input_df[5130] = input_df[118]/input_df[97]
    input_df[5131] = input_df[119]/input_df[100]
    input_df[5132] = input_df[43]/input_df[120]
    input_df[5133] = input_df[73]/input_df[121]
    input_df[5134] = input_df[104]/input_df[58]

    output_df[5125] = input_df[5125].groupby(level= 0).mean()
    output_df[5126] = input_df[5126].groupby(level= 0).mean()
    output_df[5127] = input_df[5127].groupby(level= 0).mean()
    output_df[5128] = input_df[5128].groupby(level= 0).mean()
    output_df[5129] = input_df[5129].groupby(level= 0).mean()
    output_df[5130] = input_df[5130].groupby(level= 0).mean()
    output_df[5131] = input_df[5131].groupby(level= 0).mean()
    output_df[5132] = input_df[5132].groupby(level= 0).mean()
    output_df[5133] = input_df[5133].groupby(level= 0).mean()
    output_df[5134] = input_df[5134].groupby(level= 0).mean()

    # input_df[5135] = input_df[6]/input_df[52]
    # output_df[5135] = input_df[5135].groupby(level= 0).mean()
    # output_df[5146] = input_df[22].groupby(level= 0).mean()

    commom_params = [sector_tot_id, str(date.today()), 'webforms_calc', 52]
    required_df = pd.DataFrame(columns= ['start_date', 'end_date', 'parameter_id', 'value'])
    for par_id in output_df.columns.values:
        # print(par_id)
        new_df = pd.DataFrame()
        new_df['start_date'] = Start_date
        new_df['end_date'] = End_date
        new_df['parameter_id'] = par_id
        new_df['value'] = pd.Series(output_df[par_id].values)
        required_df = pd.concat([required_df, new_df], axis= 0)

    required_df[['player_id', 'date_created', 'source', 'parametertree_id']] = commom_params
    required_df = required_df.reindex(columns= ['player_id', 'start_date', 'end_date', 'parameter_id', 'value', 'date_created', 'source', 'parametertree_id'])
    required_df.dropna(subset = ['value'], inplace = True)
    required_df = required_df.loc[~(required_df["value"] == 0)]
    data_tuples = [tuple(x) for x in required_df.to_records(index= False)]
    InsertORUpdate(data_tuples, db_conn, db_session)


# %%
def shortform_agg(sector_tot_id, db_conn, db_session):
    players = [6, 7, 8, 318]
    input_df = par_val_df(players, db_conn)
    output_df = pd.DataFrame(index=input_df.index.get_level_values(0).drop_duplicates())
    Start_date = pd.Series(output_df.index.values).apply(str)
    End_date = pd.Series(output_df.index.values).apply(end_date).apply(str)

    output_df[128] = input_df[128].groupby(level= 0).sum()

    output_df[117] = input_df[117].groupby(level= 0).sum()
    output_df[118] = input_df[118].groupby(level= 0).sum()
    output_df[119] = input_df[119].groupby(level= 0).sum()
    output_df[43] = input_df[43].groupby(level= 0).sum()
    output_df[73] = input_df[73].groupby(level= 0).sum()
    output_df[104] = input_df[104].groupby(level= 0).sum()
    output_df[137] = input_df[137].groupby(level= 0).sum()
    output_df[138] = input_df[138].groupby(level= 0).sum()
    output_df[139] = input_df[139].groupby(level= 0).sum()
    output_df[140] = input_df[140].groupby(level= 0).sum()

    output_df[35] = input_df[35].groupby(level= 0).mean()
    output_df[24] = input_df[24].groupby(level= 0).mean()

    output_df[7] = input_df[7].groupby(level= 0).sum()
    output_df[12] = input_df[12].groupby(level= 0).sum()

    output_df[18] = input_df[18].groupby(level= 0).sum()

    input_df[5125] = input_df[137]/input_df[57]
    input_df[5126] = input_df[138]/input_df[158]
    input_df[5127] = input_df[139]/input_df[159]
    input_df[5128] = input_df[140]/input_df[160]
    input_df[5129] = input_df[117]/input_df[59]
    input_df[5130] = input_df[118]/input_df[97]
    input_df[5131] = input_df[119]/input_df[100]
    input_df[5132] = input_df[43]/input_df[120]
    input_df[5133] = input_df[73]/input_df[121]
    input_df[5134] = input_df[104]/input_df[58]

    output_df[5125] = input_df[5125].groupby(level= 0).mean()
    output_df[5126] = input_df[5126].groupby(level= 0).mean()
    output_df[5127] = input_df[5127].groupby(level= 0).mean()
    output_df[5128] = input_df[5128].groupby(level= 0).mean()
    output_df[5129] = input_df[5129].groupby(level= 0).mean()
    output_df[5130] = input_df[5130].groupby(level= 0).mean()
    output_df[5131] = input_df[5131].groupby(level= 0).mean()
    output_df[5132] = input_df[5132].groupby(level= 0).mean()
    output_df[5133] = input_df[5133].groupby(level= 0).mean()
    output_df[5134] = input_df[5134].groupby(level= 0).mean()

    # input_df[5135] = input_df[6]/input_df[52]
    # output_df[5135] = input_df[5135].groupby(level= 0).mean()
    # output_df[5146] = input_df[22].groupby(level= 0).mean()

    commom_params = [sector_tot_id, str(date.today()), 'webforms_calc', 52]
    required_df = pd.DataFrame(columns= ['start_date', 'end_date', 'parameter_id', 'value'])
    for par_id in output_df.columns.values:
        # print(par_id)
        new_df = pd.DataFrame()
        new_df['start_date'] = Start_date
        new_df['end_date'] = End_date
        new_df['parameter_id'] = par_id
        new_df['value'] = pd.Series(output_df[par_id].values)
        required_df = pd.concat([required_df, new_df], axis= 0)

    required_df[['player_id', 'date_created', 'source', 'parametertree_id']] = commom_params
    required_df = required_df.reindex(columns= ['player_id', 'start_date', 'end_date', 'parameter_id', 'value', 'date_created', 'source', 'parametertree_id'])
    required_df.dropna(subset = ['value'], inplace = True)
    required_df = required_df.loc[~(required_df["value"] == 0)]
    data_tuples = [tuple(x) for x in required_df.to_records(index= False)]
    InsertORUpdate(data_tuples, db_conn, db_session)

# %%
def OTT_Audio_agg(sector_tot_id, db_conn, db_session):
    players = [16, 17, 18, 19, 21, 22, 23]
    input_df = par_val_df(players, db_conn)
    output_df = pd.DataFrame(index=input_df.index.get_level_values(0).drop_duplicates())
    Start_date = pd.Series(output_df.index.values).apply(str)
    End_date = pd.Series(output_df.index.values).apply(end_date).apply(str)

    output_df[10] = input_df[10].groupby(level= 0).sum()
    output_df[781] = input_df[781].groupby(level= 0).sum()
    output_df[782] = input_df[782].groupby(level= 0).sum()
    output_df[783] = input_df[783].groupby(level= 0).sum()

    output_df[772] = input_df[772].groupby(level= 0).sum()
    output_df[773] = input_df[773].groupby(level= 0).sum()
    output_df[775] = input_df[775].groupby(level= 0).sum()
    output_df[776] = input_df[776].groupby(level= 0).sum()
    output_df[777] = input_df[777].groupby(level= 0).sum()
    output_df[778] = input_df[778].groupby(level= 0).sum()
    output_df[779] = input_df[779].groupby(level= 0).sum()
    output_df[780] = input_df[780].groupby(level= 0).sum()

    output_df[128] = input_df[128].groupby(level= 0).sum()
 
    output_df[117] = input_df[117].groupby(level= 0).sum()
    output_df[118] = input_df[118].groupby(level= 0).sum()
    output_df[119] = input_df[119].groupby(level= 0).sum()
    output_df[43] = input_df[43].groupby(level= 0).sum()
    output_df[73] = input_df[73].groupby(level= 0).sum()
    output_df[104] = input_df[104].groupby(level= 0).sum()
    output_df[137] = input_df[137].groupby(level= 0).sum()
    output_df[138] = input_df[138].groupby(level= 0).sum()
    output_df[139] = input_df[139].groupby(level= 0).sum()
    output_df[140] = input_df[140].groupby(level= 0).sum()

    output_df[6] = input_df[6].groupby(level= 0).sum() 
    output_df[22] = input_df[22].groupby(level= 0).mean()

    output_df[35] = input_df[35].groupby(level= 0).mean()
    output_df[24] = input_df[24].groupby(level= 0).mean()

    output_df[93] = input_df[93].groupby(level= 0).sum()
    output_df[18] = input_df[18].groupby(level= 0).sum()
    output_df[75] = input_df[75].groupby(level= 0).sum()
    output_df[29] = input_df[29].groupby(level= 0).sum()

    input_df[5125] = input_df[137]/input_df[57]
    input_df[5126] = input_df[138]/input_df[158]
    input_df[5127] = input_df[139]/input_df[159]
    input_df[5128] = input_df[140]/input_df[160]
    input_df[5129] = input_df[117]/input_df[59]
    input_df[5130] = input_df[118]/input_df[97]
    input_df[5131] = input_df[119]/input_df[100]
    input_df[5132] = input_df[43]/input_df[120]
    input_df[5133] = input_df[73]/input_df[121]
    input_df[5134] = input_df[104]/input_df[58]

    input_df[5140] = input_df[781]/input_df[59]
    input_df[5141] = input_df[782]/input_df[97]
    input_df[5142] = input_df[783]/input_df[100]

    input_df[5147] = input_df[772]/input_df[58]
    input_df[5148] = input_df[773]/input_df[120]
    other_lang_streams = [x for x in range(775, 781)] 
    input_df[5154] = input_df[other_lang_streams].sum(axis= 1)/input_df[121]

    output_df[5125] = input_df[5125].groupby(level= 0).mean()
    output_df[5126] = input_df[5126].groupby(level= 0).mean()
    output_df[5127] = input_df[5127].groupby(level= 0).mean()
    output_df[5128] = input_df[5128].groupby(level= 0).mean()
    output_df[5129] = input_df[5129].groupby(level= 0).mean()
    output_df[5130] = input_df[5130].groupby(level= 0).mean()
    output_df[5131] = input_df[5131].groupby(level= 0).mean()
    output_df[5132] = input_df[5132].groupby(level= 0).mean()
    output_df[5133] = input_df[5133].groupby(level= 0).mean()
    output_df[5134] = input_df[5134].groupby(level= 0).mean()

    input_df[5135] = input_df[6]/input_df[52]
    output_df[5135] = input_df[5135].groupby(level= 0).mean()
    output_df[5146] = input_df[22].groupby(level= 0).mean()

    output_df[5147] = input_df[5147].groupby(level = 0).mean()
    output_df[5148] = input_df[5148].groupby(level = 0).mean()
    output_df[5154] = input_df[5154].groupby(level = 0).mean()

    commom_params = [sector_tot_id, str(date.today()), 'webforms_calc', 52]
    required_df = pd.DataFrame(columns= ['start_date', 'end_date', 'parameter_id', 'value'])
    for par_id in output_df.columns.values:
        # print(par_id)
        new_df = pd.DataFrame()
        new_df['start_date'] = Start_date
        new_df['end_date'] = End_date
        new_df['parameter_id'] = par_id
        new_df['value'] = pd.Series(output_df[par_id].values)
        required_df = pd.concat([required_df, new_df], axis= 0)

    required_df[['player_id', 'date_created', 'source', 'parametertree_id']] = commom_params
    required_df = required_df.reindex(columns= ['player_id', 'start_date', 'end_date', 'parameter_id', 'value', 'date_created', 'source', 'parametertree_id'])
    required_df.dropna(subset = ['value'], inplace = True)
    required_df = required_df.loc[~(required_df["value"] == 0)]
    data_tuples = [tuple(x) for x in required_df.to_records(index= False)]
    InsertORUpdate(data_tuples, db_conn, db_session)

# %%
def OTT_Video_agg(sector_tot_id, db_conn, db_session):
    players = [13, 14, 15, 29, 30, 32]
    input_df = par_val_df(players, db_conn)
    output_df = pd.DataFrame(index=input_df.index.get_level_values(0).drop_duplicates())
    Start_date = pd.Series(output_df.index.values).apply(str)
    End_date = pd.Series(output_df.index.values).apply(end_date).apply(str)

    output_df[128] = input_df[128].groupby(level= 0).sum()
 
    output_df[117] = input_df[117].groupby(level= 0).sum()
    output_df[118] = input_df[118].groupby(level= 0).sum()
    output_df[119] = input_df[119].groupby(level= 0).sum()
    output_df[43] = input_df[43].groupby(level= 0).sum()
    output_df[73] = input_df[73].groupby(level= 0).sum()
    output_df[104] = input_df[104].groupby(level= 0).sum()
    output_df[137] = input_df[137].groupby(level= 0).sum()
    output_df[138] = input_df[138].groupby(level= 0).sum()
    output_df[139] = input_df[139].groupby(level= 0).sum()
    output_df[140] = input_df[140].groupby(level= 0).sum()

    output_df[6] = input_df[6].groupby(level= 0).sum() 
    output_df[22] = input_df[22].groupby(level= 0).mean()

    output_df[35] = input_df[35].groupby(level= 0).mean()
    output_df[24] = input_df[24].groupby(level= 0).mean()

    output_df[93] = input_df[93].groupby(level= 0).sum()
    output_df[18] = input_df[18].groupby(level= 0).sum()
    output_df[75] = input_df[75].groupby(level= 0).sum()
    output_df[29] = input_df[29].groupby(level= 0).sum()

    input_df[5125] = input_df[137]/input_df[57]
    input_df[5126] = input_df[138]/input_df[158]
    input_df[5127] = input_df[139]/input_df[159]
    input_df[5128] = input_df[140]/input_df[160]
    input_df[5129] = input_df[117]/input_df[59]
    input_df[5130] = input_df[118]/input_df[97]
    input_df[5131] = input_df[119]/input_df[100]
    input_df[5132] = input_df[43]/input_df[120]
    input_df[5133] = input_df[73]/input_df[121]
    input_df[5134] = input_df[104]/input_df[58]

    output_df[5125] = input_df[5125].groupby(level= 0).mean()
    output_df[5126] = input_df[5126].groupby(level= 0).mean()
    output_df[5127] = input_df[5127].groupby(level= 0).mean()
    output_df[5128] = input_df[5128].groupby(level= 0).mean()
    output_df[5129] = input_df[5129].groupby(level= 0).mean()
    output_df[5130] = input_df[5130].groupby(level= 0).mean()
    output_df[5131] = input_df[5131].groupby(level= 0).mean()
    output_df[5132] = input_df[5132].groupby(level= 0).mean()
    output_df[5133] = input_df[5133].groupby(level= 0).mean()
    output_df[5134] = input_df[5134].groupby(level= 0).mean()

    input_df[5135] = input_df[6]/input_df[52]
    output_df[5135] = input_df[5135].groupby(level= 0).mean()
    output_df[5146] = input_df[22].groupby(level= 0).mean()

    commom_params = [sector_tot_id, str(date.today()), 'webforms_calc', 52]
    required_df = pd.DataFrame(columns= ['start_date', 'end_date', 'parameter_id', 'value'])
    for par_id in output_df.columns.values:
        # print(par_id)
        new_df = pd.DataFrame()
        new_df['start_date'] = Start_date
        new_df['end_date'] = End_date
        new_df['parameter_id'] = par_id
        new_df['value'] = pd.Series(output_df[par_id].values)
        required_df = pd.concat([required_df, new_df], axis= 0)

    required_df[['player_id', 'date_created', 'source', 'parametertree_id']] = commom_params
    required_df = required_df.reindex(columns= ['player_id', 'start_date', 'end_date', 'parameter_id', 'value', 'date_created', 'source', 'parametertree_id'])
    required_df.dropna(subset = ['value'], inplace = True)
    required_df = required_df.loc[~(required_df["value"] == 0)]
    data_tuples = [tuple(x) for x in required_df.to_records(index= False)]
    InsertORUpdate(data_tuples, db_conn, db_session)
    


if __name__ == "__main__":
    database_name = db_settings['NAME']
    db_session, db_conn = get_db_connection(database_name)
    try:
        CSM_agg(37, db_conn, db_session)
    except KeyError as e:
        print(e)
        pass
    try:
        shortform_agg(36, db_conn, db_session)
    except KeyError as e:
        print(e)
        pass
    try:
        OTT_Audio_agg(35, db_conn, db_session)
    except KeyError as e:
        print(e)
        pass
    try:
        OTT_Video_agg(34, db_conn, db_session)
    except KeyError as e:
        print(e)
        pass

# %%



