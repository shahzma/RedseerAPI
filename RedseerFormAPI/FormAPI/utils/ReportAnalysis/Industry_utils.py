from FormAPI.utils.ReportAnalysis.Content_sector_total import CSM_agg, shortform_agg, OTT_Audio_agg, OTT_Video_agg
from FormAPI.utils.ReportAnalysis.Foodtech_sector_total import Foodtech_aggregate
from FormAPI.utils.ReportAnalysis.Mobility_sector_total import Mobility_aggregate, Citywise_agg  
from FormAPI.utils.ReportAnalysis.common_func import par_val_df, InsertORUpdate, get_db_connection

def Prelim_calculation(industry_id):
    if industry_id==13:
        return lambda tot_player, db_conn, db_session: Foodtech_aggregate(tot_player, db_conn, db_session)
    elif industry_id==35:
        return lambda tot_player, db_conn, db_session: Mobility_aggregate(tot_player, db_conn, db_session)
    elif industry_id==3:
        return lambda tot_player, db_conn, db_session: CSM_agg(tot_player, db_conn, db_session)
    elif industry_id==4:
        return lambda tot_player, db_conn, db_session: shortform_agg(tot_player, db_conn, db_session)
    elif industry_id==2:
        return lambda tot_player, db_conn, db_session: OTT_Audio_agg(tot_player, db_conn, db_session)
    elif industry_id==1:
        return lambda tot_player, db_conn, db_session: OTT_Video_agg(tot_player, db_conn, db_session)
    else:
        raise ValueError("Invalid industry name")