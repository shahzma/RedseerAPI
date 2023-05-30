# %%
from sqlalchemy.orm import sessionmaker, Session
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
# import User-defined functions/methods
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
def Foodtech_aggregate(sector_tot_id, db_conn, db_session):
    # get parameter wise data for the players
    players = [45, 46]
    input_df = par_val_df(players, db_conn)
    output_df = par_val_df([sector_tot_id], db_conn)
    output_df = output_df.droplevel('player_id')
    Start_date = pd.Series(output_df.index.values).apply(str)
    End_date = pd.Series(output_df.index.values).apply(end_date).apply(str)
    # Calculation for GOV broken down by Ciy tiers
    
    input_df[346] = input_df[3197] / input_df[3197].groupby(level= 0).sum()
    input_df[1607] = input_df[3183] / input_df[3183].groupby(level= 0).sum()
    input_df[1608] = input_df[3184] / input_df[3184].groupby(level= 0).sum()
    input_df[1609] = input_df[3185] / input_df[3185].groupby(level= 0).sum()
    input_df[1610] = input_df[3186] / input_df[3186].groupby(level= 0).sum()

    output_df[366] = (input_df[346] * input_df[366]).groupby(level= 0).sum()
    # output_df[341] = (input_df[341] * input_df[346])
    output_df[371] = input_df[371].groupby(level = 0).sum()
    output_df[1623] = (input_df[1607] * input_df[1623]).groupby(level= 0).sum()  
    output_df[1624] = (input_df[1608] * input_df[1624]).groupby(level= 0).sum()  
    output_df[1625] = (input_df[1609] * input_df[1625]).groupby(level= 0).sum()  
    output_df[1626] = (input_df[1610] * input_df[1626]).groupby(level= 0).sum()  
    output_df[3183] = input_df[3183].groupby(level= 0).sum()
    output_df[3184] = input_df[3184].groupby(level= 0).sum()
    output_df[3185] = input_df[3185].groupby(level= 0).sum()
    output_df[3186] = input_df[3186].groupby(level= 0).sum()

    output_df[3689] = input_df[3689].groupby(level = 0).sum()
    output_df[3690] = input_df[3690].groupby(level = 0).sum()

    output_df[1332] = input_df[3197].groupby(level = 0).sum()/(0.75 *input_df[238]).groupby(level = 0).sum()/10**3

    output_df[1718] = (input_df[346] * input_df[1718]).groupby(level = 0).sum()    
    output_df[1719] = (input_df[346] * input_df[1719]).groupby(level = 0).sum()    
    output_df[420] = (input_df[346] * input_df[420]).groupby(level = 0).sum()

    output_df[3456] = input_df[3456].groupby(level = 0).sum()
    output_df[3457] = input_df[3457].groupby(level = 0).sum()
    output_df[3458] = input_df[3458].groupby(level = 0).sum()
    output_df[3459] = input_df[3459].groupby(level = 0).sum()

    output_df[417] = (input_df[346] * input_df[417]).groupby(level = 0).sum()
    output_df[1729] = (input_df[346] * input_df[1729]).groupby(level = 0).sum()
    output_df[1727] = (input_df[346] * input_df[1727]).groupby(level = 0).sum()
    output_df[420] = (input_df[346] * input_df[420]).groupby(level = 0).sum()
    output_df[421] = (input_df[346] * input_df[421]).groupby(level = 0).sum()
    output_df[422] = (input_df[346] * input_df[422]).groupby(level = 0).sum()
    output_df[1730] = output_df[420] + output_df[421] + output_df[422]

    output_df[320] = input_df[320].groupby(level= 0).mean()
    output_df[321] = input_df[321].groupby(level= 0).mean()
    output_df[322] = input_df[322].groupby(level= 0).mean()
    output_df[327] = input_df[327].groupby(level= 0).mean()
    output_df[328] = input_df[328].groupby(level= 0).mean()
    output_df[329] = input_df[329].groupby(level= 0).mean()
    output_df[330] = input_df[330].groupby(level= 0).mean()
    output_df[331] = input_df[331].groupby(level= 0).mean()

    output_df[332] = input_df[332].groupby(level= 0).sum()
    output_df[333] = input_df[333].groupby(level= 0).mean()
    output_df[335] = input_df[335].groupby(level= 0).mean()

    output_df[5121] = output_df[3183]/output_df[4037]/10**3
    output_df[5122] = output_df[3184]/output_df[4038]/10**3
    output_df[5123] = output_df[3185]/output_df[4039]/10**3
    output_df[5124] = output_df[3186]/output_df[4040]/10**3

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
if __name__ == "__main__":
    database_name = db_settings['NAME']
    db_session, db_conn = get_db_connection(database_name)
    Foodtech_aggregate(286, db_conn, db_session)



# %%
