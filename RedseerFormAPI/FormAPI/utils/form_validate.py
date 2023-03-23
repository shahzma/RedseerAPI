# from sklearn import metrics, linear_model
# import matplotlib.pyplot as plt
import pandas as pd
import pymysql
from django.conf import settings
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime, date
import math

db_settings = settings.DATABASES['default']


class ValidateForm:

    def get_connection_url(self):
        package = "mysql+pymysql"
        database_connection_url = f"{package}://{db_settings['USER']}:{db_settings['PASSWORD']}@{db_settings['HOST']}:{db_settings['PORT']}/{db_settings['NAME']}"
        return database_connection_url

    def get_db_connection(self):
        database_connection_url = self.get_connection_url()
        connect_args = {'charset': 'latin1'}
        # connect_args = {'ssl': {'ttls': True}}
        engine = create_engine(database_connection_url,
                               echo=False, connect_args=connect_args)
        db_conn = engine.connect()

        dbSession = sessionmaker(bind=engine)
        db_session = dbSession()

        return db_session, db_conn

    def self_trend_anomaly(self, player_id, reference_date, player_main_df):
        AP_df_rows = []
        # Determine whether the reference month data point for every ("player_id", "parameter_id") could be anomalous
        for key, value_df in player_main_df.groupby("parameter_id"):
            try:

                parameter_id = key
                # change_1 = % change from last_month to reference month
                # threshold_1 = last 12 months average % change(X_avg) +/- 2* std_for_last_12_months (excludes change_1)
                value_df.sort_values("start_date", inplace=True)
                # reference_date = pd.to_datetime(value_df["start_date"].iloc[-1])
                ref_mon_value = value_df[value_df["start_date"]
                                         == reference_date]["value"].iloc[0]
                previous_year_date = date(
                    reference_date.year - 1, reference_date.month, 1)

                value_df["pct_change"] = value_df["value"].pct_change()
                # take out MoM change for last 13 months (reference month + last 12 months)
                last_13_months_MoM_change = value_df["pct_change"].iloc[-13:]
                ref_month_change = last_13_months_MoM_change.iloc[-1]
                last_12_months_MoM_change = last_13_months_MoM_change.iloc[:-1]

                std_last_12_months = last_12_months_MoM_change.std()
                no_of_std = 2
                threshold_1_UB = last_12_months_MoM_change.mean() + no_of_std * \
                    std_last_12_months
                threshold_1_LB = last_12_months_MoM_change.mean() - no_of_std * \
                    std_last_12_months

                # threshold_2 -> % change from last_month to reference month for the previous year
                del_change_t1 = value_df[value_df["start_date"]
                                         == previous_year_date]["pct_change"].iloc[0]
                print(del_change_t1)
                pv_change_factor = 0.2
                threshold_2_UB = del_change_t1*(1 + pv_change_factor)
                threshold_2_LB = del_change_t1*(1 - pv_change_factor)
                boolean_exp_1 = (ref_month_change > threshold_1_UB) | (
                    ref_month_change < threshold_1_LB)
                boolean_exp_2 = (ref_month_change > threshold_2_UB) | (
                    ref_month_change < threshold_2_LB)

                if boolean_exp_1:  # Past trend anomaly
                    Self_trend_anomaly = "Yes"
                else:
                    Self_trend_anomaly = "No"

                # Determine if the player is showing anomalous behaviour wrt overall industry behaviour for the reference month
                """ ref_mon_ind_chg = ind_anomaly_df[ind_anomaly_df["parameter_id"] == parameter_id]["ind_avg_change"].iloc[0]
                ind_dev_factor = 0.2
                threshold_3_UB = ref_mon_ind_chg * (1 + ind_dev_factor)
                threshold_3_LB = ref_mon_ind_chg * (1 - ind_dev_factor)
                if (ref_month_change > threshold_3_UB) | (ref_month_change < threshold_3_LB):
                    # Anomaly_wrt_industry
                    Anomaly_wrt_industry = "Yes"
                else:
                    Anomaly_wrt_industry = "No" """

                if math.isnan(del_change_t1):
                    Seasonality_anomaly = "No"
                else:
                    if boolean_exp_2:  # Seasonality anomaly
                        Seasonality_anomaly = "Yes"
                    else:
                        Seasonality_anomaly = "No"

                current_row = {"player_id": player_id, "parameter_id": parameter_id, "ref_date": reference_date, "value": ref_mon_value, "Self_trend_anomaly": Self_trend_anomaly,
                               "Seasonality_anomaly": Seasonality_anomaly}
                AP_df_rows.append(current_row)

            except:
                continue
        Anomaly_Prediction_df = pd.DataFrame.from_dict(AP_df_rows)
        return Anomaly_Prediction_df

    def final_classification(self, Anomaly_Prediction_df, player_id):
        corr_df = pd.read_csv(os.path.join(settings.BASE_DIR, './FormAPI/utils/corr_df.csv')).query(
            "player_id == " + str(player_id))
        Actual_Observed_Anomaly = []
        for key, value_df in Anomaly_Prediction_df.groupby("parameter_id"):
            try:
                parameter_id = key
                indicative_state = (value_df["Self_trend_anomaly"].iloc[0] == "Yes") | (
                    value_df["Seasonality_anomaly"].iloc[0] == "Yes")

                # if the label is "Potential Anomaly", then calculate the number of corr_params which have the "Anomaly_state" = "Potential Anomaly"
                # No need if the Anomaly_Prediction_df is already filtered for "Potential Anomaly" state
                # if more than half the corr_parameters are potenially anomalous then mark the data point as "Actual Observed Anomaly" otherwise keep the original label
                if indicative_state:
                    corr_params_series = corr_df[(
                        corr_df["parameter_id"] == parameter_id)]["corr_param_id"]
                    total_corr_params = len(corr_params_series)
                    anomaly_state_count = len(Anomaly_Prediction_df[(Anomaly_Prediction_df["parameter_id"].isin(corr_params_series)) & (
                        (Anomaly_Prediction_df["Self_trend_anomaly"] == "Yes") | (Anomaly_Prediction_df["Seasonality_anomaly"] == "Yes"))])
                    corr_anomaly_fraction = anomaly_state_count/total_corr_params
                    if corr_anomaly_fraction > 0.6:
                        Actual_Observed_Anomaly.append("Yes")
                    else:
                        Actual_Observed_Anomaly.append("No")
                else:
                    Actual_Observed_Anomaly.append("No")

            except Exception as e:
                print(e)
                Actual_Observed_Anomaly.append("No")
                continue

        Anomaly_Prediction_df["Actual_Observed_Anomaly"] = Actual_Observed_Anomaly
        Anomaly_Prediction_df = Anomaly_Prediction_df[['player_id', 'player_name', 'parameter_id', 'ref_date', 'value',
                                                       'parameter_name', 'parent_parameter', 'Self_trend_anomaly', 'Seasonality_anomaly', 'Actual_Observed_Anomaly']]
        Anomaly_Prediction_df['anomaly_warnings'] = Anomaly_Prediction_df[[
            'Self_trend_anomaly', 'Seasonality_anomaly', 'Actual_Observed_Anomaly']].apply(lambda x: self.warning(x), axis=1)
        return Anomaly_Prediction_df

    def warning(self, df_row):
        warning = ""
        i = 0
        if df_row['Self_trend_anomaly'] == "Yes":
            i += 1
            warning += str(i) + ") The current month change in parameter value deviates from its last 12 month trend"
            warning += "\n"
        if df_row['Seasonality_anomaly'] == "Yes":
            i += 1
            warning += str(i) + ") The MoM change in parameter value significantly deviates from that for the previous year"
            warning += "\n"
        if df_row['Actual_Observed_Anomaly'] == "Yes":
            i += 1
            warning += str(i) + ") It seems many strongly correlated parameters have also changed in line with their direction of correlation"
        return warning

    # Take user input

    def find_anomalies(self, webform_dict):
        # global player_id, reference_date
        database_name = "content_data"
        # db_session, db_conn = self.get_db_connection()
        db_session, db_conn = self.get_db_connection()

        players_df = pd.read_sql(text(
            "SELECT player_id, player_name, industry_id FROM player"), db_conn)
        industry_df = pd.read_sql(
            text("SELECT industry_id, industry_name from content_data.industry"), db_conn)
        parameter_df = pd.read_sql(text(
            "SELECT parameter_id, parameter_name, parent_parameter FROM content_data.parameter"), db_conn)
        player_name = webform_dict["playerName"]
        player_id = players_df[players_df['player_name']
                               == player_name]['player_id'].iloc[0]

        main_df = pd.read_sql(text(
            "SELECT * FROM main_data where player_id = " + str(player_id)), db_conn)
        filter_main_df = main_df[["player_id", "industry_id",
                                  "parameter_id", "start_date", "end_date", "value", "source"]]
        exclusion_list = ["webforms_calc", "webforms calc",
                          "webform_calc", "weight_avg", "Keyboard"]
        filter_main_df = filter_main_df[~filter_main_df["source"].isin(
            exclusion_list)]

        webform_date = datetime.strptime(
            webform_dict['createdDate'], '%Y-%m-%d')
        if webform_date.month != 1:
            ref_month = webform_date.month - 1
            ref_year = webform_date.year
        else:
            ref_month = 12
            ref_year = webform_date.year - 1
        reference_date = date(ref_year, ref_month, 1)
        parameter_list = [id_value for id_value in webform_dict['parameters']
                          if not id_value.get('isAnomalyDismissed', True)]
        # print(parameter_list)
        if not parameter_list:  # case when all are isAnomalyDismissed=true,=> empty parameter_list
            return []
        webform_df = pd.DataFrame.from_dict(
            parameter_list).drop('isAnomalyDismissed', axis=1)
        webform_df.rename(columns={"id": "parameter_id"}, inplace=True)
        webform_df['start_date'] = reference_date
        webform_df['player_id'] = player_id
        player_main_df = filter_main_df[(filter_main_df["player_id"] == player_id) & (
            filter_main_df["start_date"] <= reference_date) & filter_main_df['parameter_id'].isin(webform_df['parameter_id'])]
        player_main_df = player_main_df[[
            "player_id", "parameter_id", "start_date", "value"]]
        # ind_anomaly_df = industry_trend(player_id, reference_date, webform_df)
        player_main_df = pd.concat([player_main_df, webform_df], axis=0)
        Anomaly_Prediction_df = self.self_trend_anomaly(
            player_id, reference_date, player_main_df)

        if Anomaly_Prediction_df.empty:
            return []
        else:
            Anomaly_Prediction_df = pd.merge(
                Anomaly_Prediction_df, parameter_df, on="parameter_id", how="left")
            Anomaly_Prediction_df = pd.merge(
                Anomaly_Prediction_df, players_df, on="player_id", how="left")
            Anomaly_Prediction_df = self.final_classification(
                Anomaly_Prediction_df, player_id)
            # print(Anomaly_Prediction_df)
            return Anomaly_Prediction_df[['parameter_id', 'anomaly_warnings']].to_dict(orient='records')
