import pandas as pd
import os
import pymysql
import calendar
import pymysql
import requests
import json
import msal

import datetime
from datetime import datetime
from datetime import date
import calendar
from calendar import monthrange
from django.conf import settings
import sys

db_settings = settings.DATABASES['default']

class CalculatedParamMobilityFn:
    global max_par
    def __init__(self):
        #One Drive Connection for WA
        self.CLIENT_ID = 'fc1cef01-9962-458e-a314-4e31a3d10791'
        self.TENANT_ID= '00a9ff8c-9830-4847-ae51-4579ec092cb4'
        
        self.AUTHORITY_URL = 'https://login.microsoftonline.com/00a9ff8c-9830-4847-ae51-4579ec092cb4'
        
        self.RESOURCE_URL = 'https://graph.microsoft.com/'
        self.API_VERSION = 'v1.0'
        self.USERNAME = 'operations@redseerconsulting.com' #Office365 user's account username
        self.PASSWORD = 'BM@OPS@123'
        self.SCOPES = ['Sites.ReadWrite.All','Files.ReadWrite.All']
        self.file_name = "Weighted Average Parameters - Benchmarks Sectors.xlsx"
        
        

    @staticmethod
    def month_range(sd):
        yr = int(sd[:4])
        month = int(sd[5:7])
        Total_number_days = calendar.monthrange(yr, month)[1]
        return Total_number_days
    @staticmethod
    def pr_sd(sd):#previous start date calculation
        year, month, day = sd.year, sd.month, sd.day
        if month == 1:
            return date(year - 1, 12, day)
        else:
            return date(year, month - 1, day)

    @staticmethod
    def pr_ed(ed):#previous end date calculation
        year, month, day = ed.year, ed.month, ed.day
        if month == 1:
            #print(input_date)
            pr_year=year-1
            
            pr_day = calendar.monthrange(pr_year, 12)
            #print(pr_day[1])
            return date(pr_year, 12, pr_day[1])
        else:
            pr_day = calendar.monthrange(year, month-1)
            #print(input_date)
            return date(year, month - 1, pr_day[1])
        
    @staticmethod
    def InsertORUpdate(data):
        try:
            db = pymysql.connect(
                host=db_settings['HOST'],
                port=int(db_settings['PORT']),
                user=db_settings['USER'],
                password=db_settings['PASSWORD'],
                db=db_settings['NAME'],
                ssl={'ssl': {'tls': True}}
            )

            cur = db.cursor()
            query = """
            INSERT INTO main_data (
                player_id, start_date, end_date, parameter_id, value, date_created, source, parametertree_id, report_version_id
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) as value_list
            ON DUPLICATE KEY UPDATE value = value_list.value, date_created = value_list.date_created, report_version_id = value_list.report_version_id
            """
            cur.executemany(query, data)
            db.commit()
            print("Mobility Script:- InsertORUpdate finished")
        except Exception as e:
            print("Mobility Script:- Error in InsertORUpdate:- ", e)

    @staticmethod
    def par_val_dict(pl_id, sd, ed, db, id_name_dict):
        try:
            cur = db.cursor()
            s = "select * from main_data where player_id='" + str(pl_id
                                                                  ) + "' and start_date='" + str(sd) + "' and end_date='" + str(ed
                                                                                                                                ) + "';"
            cur.execute(s)
            d = cur.fetchall()
            dat = pd.DataFrame.from_dict(d)
            dat = dat[[4, 5]]
            dat = dat.rename(columns={(4): 'par_id', (5): 'val'})
            ans = zip(dat.par_id, dat.val)
            ans = dict(ans)
            cur.close()
            input_dict = {}
            for i in id_name_dict:
                try:
                    ans[i]
                    input_dict[id_name_dict[i]] = ans[i]
                except:
                    input_dict[id_name_dict[i]] = 0
            print("Mobility Script:- par_val_dict finished")
            return input_dict
        except Exception as e:
            print("Mobility Script:- Error in par_val_dict:- ", e)
    
    def reset_calc_dict(self, id_name_dict):
        try:
            in_values = [None] * len(id_name_dict)
            calc_dict = dict(zip(list(id_name_dict.values()), in_values))
            print("Mobility Script:- reset_calc_dict finished")
            return calc_dict
        except Exception as e:
            print("Mobility Script:- Error in reset_calc_dict:- ", e)

    #Connecting with the drive
    # global CLIENT_ID,TENANT_ID,AUTHORITY_URL,RESOURCE_URL,API_VERSION,USERNAME,PASSWORD,SCOPES,file_name
    # CLIENT_ID = 'fc1cef01-9962-458e-a314-4e31a3d10791'
    # TENANT_ID= '00a9ff8c-9830-4847-ae51-4579ec092cb4'
    # # CLIENT_SECRET = '3c27dc10-61ce-4d9b-baa7-b4c7f94aa346'
    # AUTHORITY_URL = 'https://login.microsoftonline.com/00a9ff8c-9830-4847-ae51-4579ec092cb4'
    # # AUTHORITY_URL = 'https://login.microsoftonline.com/{}'.format(TENANT_ID)
    # RESOURCE_URL = 'https://graph.microsoft.com/'
    # API_VERSION = 'v1.0'
    # USERNAME = 'operations@redseerconsulting.com' #Office365 user's account username
    # PASSWORD = 'BM@OPS@123'
    # SCOPES = ['Sites.ReadWrite.All','Files.ReadWrite.All'] # Add other scopes/permissions as needed.

    #Defining func for WA sheet
    
    def upload_resumable2(self, file_name):
        try:
            # Creating a public client app, Aquire an access token for the user and set the header for API calls
            cognos_to_onedrive = msal.PublicClientApplication(self.CLIENT_ID, authority=self.AUTHORITY_URL)
            token = cognos_to_onedrive.acquire_token_by_username_password(self.USERNAME,self.PASSWORD,self.SCOPES)
            header = {'Authorization': 'Bearer {}'.format(token['access_token'])}
            # download 
            response = requests.get(
                    '{}/{}/me/drive/root:/Product Data Excels (Do not Touch)/Calculated_parameter_sheets'
                    .format(self.RESOURCE_URL, self.API_VERSION) + '/' + file_name + ':/content',
                    headers=header)
            
            
            print("Mobility Script:- upload_resumable2 finished")
            return response.content
        except Exception as e:
            print("Mobility Script:- Error in upload_resumable2:- ", e)



    # file_name = "Weighted Average Parameters - Benchmarks Sectors.xlsx"                     #data File name
    # #print(file_name)

    # conflict_resolve = {
    # "item": {
    #     "@microsoft.graph.conflictBehavior": "replace"
    # }
    # }
    

    
    def WA_Calc(self, player_id, df, sd, ed, db, rep_ver_id):
        try:
            required_rows = []
            dt = pd.Timestamp.today().date()
            dt = str(dt)
            cur = db.cursor()
            print('player = ', player_id)
            for k in range(1, len(df)):
                par_id = df.iloc[k, 0]
                if str(par_id) == 'nan':
                    continue
                par1 = df.iloc[k, 4]
                par2 = df.iloc[k, 5]
                par3 = df.iloc[k, 6]
                A = "SELECT value from main_data WHERE player_id= '" + str(player_id
                                                                           ) + "' AND start_date= '" + str(sd
                                                                                                           ) + "'" + " AND end_date='" + str(ed
                                                                                                                                             ) + "'" + " AND parameter_id='" + str(par1) + "';"
                cur.execute(A)
                to = cur.fetchall()
                to = pd.DataFrame.from_dict(to)
                par_1 = 0
                par_2 = 0
                if len(to) != 0:
                    par_1 = to.iat[0, 0]
                if str(par2) == 'no_days':
                    par_2 = self.month_range(str(sd))
                else:
                    B = "SELECT value from main_data WHERE player_id= '" + str(
                        player_id) + "' AND start_date= '" + str(sd
                                                                 ) + "'" + " AND end_date='" + str(ed
                                                                                                   ) + "'" + " AND parameter_id='" + str(par2) + "';"
                    cur.execute(B)
                    to = cur.fetchall()
                    to = pd.DataFrame.from_dict(to)
                    if len(to) != 0:
                        par_2 = to.iat[0, 0]
                if str(par3) == 'nan':
                    val = par_1 * par_2
                else:
                    val = par_1 * par_2
                    val = val / 100
                if val != 0:
                    data_dict = {'player_id': player_id, 'start_date': sd,
                                 'end_date': ed, 'parameter_id': par_id, 'value': val,
                                 'date_created': dt, 'source': 'weight_avg',
                                 'parametertree_id': 52, 'report_version_id': rep_ver_id}
                    required_rows.append(tuple(data_dict.values()))
            cur.close()    
            self.InsertORUpdate(required_rows)
            print("Mobility Script:- WA_Calc finished")
        except Exception as e:
            print("Mobility Script:- Error in WA_Calc:- ", e)

    def get_WA_sheet(self, sheet_name):
        try:
            yls2 = self.upload_resumable2(self.file_name)
            WA_input_df = pd.read_excel(
                yls2, sheet_name, header=None, index_col=False)
            print("Mobility Script:- get_WA_sheet finished")
            return WA_input_df
        except Exception as e:
            print("Mobility Script:- Error in get_WA_sheet:- ", e)

    def calc_script(self, pl_id, sd, ed, db, id_name_dict, rep_ver_id):
        try:
            calc_dict = {}
            d = self.par_val_dict(pl_id, sd, ed, db, id_name_dict)
            try:
                calc_dict['1971:Total(Mn)'] = d['1972:Cab Total(Mn)'] + d[
                    '2070:Auto Total(Mn)'] + d['2084:Moto Total(Mn)']
                calc_dict['1973:P2P(Mn)'] = d['1974:P2P(%)'] * d[
                    '1972:Cab Total(Mn)'] / 100
                calc_dict['1975:Outstation(Mn)'] = d['1976:Outstation(%)'] * d[
                    '1972:Cab Total(Mn)'] / 100
                if calc_dict['1973:P2P(Mn)'] != 0 or calc_dict[
                    '1975:Outstation(Mn)'] != 0:
                    calc_dict['1977:Rental(Mn)'] = d['1972:Cab Total(Mn)'
                        ] - calc_dict['1973:P2P(Mn)'] - calc_dict[
                        '1975:Outstation(Mn)']
                calc_dict['1978:Rental(%)'] = calc_dict['1977:Rental(Mn)'] / d[
                    '1972:Cab Total(Mn)'] * 100
                calc_dict['1980:Mini(%)'] = d['1979:Mini(Mn)'] / d[
                    '1972:Cab Total(Mn)'] * 100
                calc_dict['1982:Prime(%)'] = d['1981:Prime(Mn)'] / d[
                    '1972:Cab Total(Mn)'] * 100
                calc_dict['1984:Play(%)'] = d['1983:Play(Mn)'] / d[
                    '1972:Cab Total(Mn)'] * 100
                calc_dict['1985:SUV(Mn)'] = d['1972:Cab Total(Mn)'] - d[
                    '1979:Mini(Mn)'] - d['1981:Prime(Mn)'] - d['1983:Play(Mn)']
                calc_dict['1986:SUV(%)'] = calc_dict['1985:SUV(Mn)'] / d[
                    '1972:Cab Total(Mn)'] * 100
                calc_dict['1987:Top 7(Mn)'] = d['1994:Delhi NCR(Mn)'] + d[
                    '2003:Mumbai(Mn)'] + d['2012:Bangalore(Mn)'] + d[
                    '2021:Kolkata(Mn)'] + d['2030:Hyderabad(Mn)'] + d[
                    '2039:Chennai(Mn)'] + d['2048:Pune(Mn)']
                calc_dict['1988:Top 7(%)'] = calc_dict['1987:Top 7(Mn)'] / d[
                    '1972:Cab Total(Mn)'] * 100
                calc_dict['1989:Top 8-19(Mn)'] = d['2057:Lucknow(Mn)'] + d[
                    '2058:Jaipur(Mn)'] + d['2059:Chandigarh(Mn)'] + d[
                    '2060:Ahmedabad(Mn)'] + d['2061:Nagpur(Mn)'] + d[
                    '2062:Bhopal(Mn)'] + d['2063:Patna(Mn)'] + d['2064:Ranchi(Mn)'
                    ] + d['2065:Guwahati(Mn)'] + d['2066:Kanpur(Mn)'] + d[
                    '2067:Dehradun(Mn)'] + d['2068:Coimbatore(Mn)']
                calc_dict['1990:Top 8-19(%)'] = calc_dict['1989:Top 8-19(Mn)'] / d[
                    '1972:Cab Total(Mn)'] * 100
                if calc_dict['1987:Top 7(Mn)'] != 0 or calc_dict[
                    '1989:Top 8-19(Mn)'] != 0:
                    calc_dict['1991:Rest +19(Mn)'] = d['1972:Cab Total(Mn)'
                        ] - calc_dict['1987:Top 7(Mn)'] - calc_dict[
                        '1989:Top 8-19(Mn)']
            except:
                pass
            try:
                calc_dict['1992:Rest +19(%)'] = calc_dict['1991:Rest +19(Mn)'] / d[
                    '1972:Cab Total(Mn)'] * 100
            except:
                pass
            try:
                if d['1999:Mini(%)'] != 0 and d['2000:Prime(%)'] != 0 and d[
                    '2001:Play(%)'] != 0:
                    calc_dict['2002:SUV(%)'] = 100 - d['1999:Mini(%)'] - d[
                        '2000:Prime(%)'] - d['2001:Play(%)']
            except:
                pass
            try:
                if d['2008:Mini(%)'] != 0 or d['2009:Prime(%)'] != 0 or d[
                    '2010:Play(%)'] != 0:
                    calc_dict['2011:SUV(%)'] = 100 - d['2008:Mini(%)'] - d[
                        '2009:Prime(%)'] - d['2010:Play(%)']
            except:
                pass
            try:
                if d['2017:Mini(%)'] != 0 and d['2018:Prime(%)'] != 0 and d[
                    '2019:Play(%)'] != 0:
                    calc_dict['2020:SUV(%)'] = 100 - d['2017:Mini(%)'] - d[
                        '2018:Prime(%)'] - d['2019:Play(%)']
            except:
                pass
            try:
                if d['2026:Mini(%)'] != 0 and d['2027:Prime(%)'] != 0 and d[
                    '2028:Play(%)'] != 0:
                    calc_dict['2029:SUV(%)'] = 100 - d['2026:Mini(%)'] - d[
                        '2027:Prime(%)'] - d['2028:Play(%)']
            except:
                pass
            try:
                if d['2035:Mini(%)'] != 0 and d['2036:Prime(%)'] != 0 and d[
                    '2037:Play(%)'] != 0:
                    calc_dict['2038:SUV(%)'] = 100 - d['2035:Mini(%)'] - d[
                        '2036:Prime(%)'] - d['2037:Play(%)']
            except:
                pass
            try:
                if d['2044:Mini(%)'] != 0 and d['2045:Prime(%)'] != 0 and d[
                    '2046:Play(%)'] != 0:
                    calc_dict['2047:SUV(%)'] = 100 - d['2044:Mini(%)'] - d[
                        '2045:Prime(%)'] - d['2046:Play(%)']
            except:
                pass
            try:
                if d['2053:Mini(%)'] != 0 and d['2054:Prime(%)'] != 0 and d[
                    '2055:Play(%)'] != 0:
                    calc_dict['2056:SUV(%)'] = 100 - d['2053:Mini(%)'] - d[
                        '2054:Prime(%)'] - d['2055:Play(%)']
            except:
                pass
            try:
                if d['1995:P2P(Mn)'] != 0 and d['1996:Outstation(Mn)'] != 0:
                    calc_dict['1997:Rental(Mn)'] = d['1994:Delhi NCR(Mn)'] - d[
                        '1995:P2P(Mn)'] - d['1996:Outstation(Mn)']
            except:
                pass
            try:
                if d['2004:P2P(Mn)'] != 0 and d['2005:Outstation(Mn)'] != 0:
                    calc_dict['2006:Rental(Mn)'] = d['2003:Mumbai(Mn)'] - d[
                        '2004:P2P(Mn)'] - d['2005:Outstation(Mn)']
            except:
                pass
            try:
                if d['2013:P2P(Mn)'] != 0 and d['2014:Outstation(Mn)'] != 0:
                    calc_dict['2015:Rental(Mn)'] = d['2012:Bangalore(Mn)'] - d[
                        '2013:P2P(Mn)'] - d['2014:Outstation(Mn)']
            except:
                pass
            try:
                if d['2022:P2P(Mn)'] != 0 and d['2023:Outstation(Mn)'] != 0:
                    calc_dict['2024:Rental(Mn)'] = d['2021:Kolkata(Mn)'] - d[
                        '2022:P2P(Mn)'] - d['2023:Outstation(Mn)']
            except:
                pass
            try:
                if d['2031:P2P(Mn)'] != 0 and d['2032:Outstation(Mn)'] != 0:
                    calc_dict['2033:Rental(Mn)'] = d['2030:Hyderabad(Mn)'] - d[
                        '2031:P2P(Mn)'] - d['2032:Outstation(Mn)']
            except:
                pass
            try:
                if d['2040:P2P(Mn)'] != 0 and d['2041:Outstation(Mn)'] != 0:
                    calc_dict['2042:Rental(Mn)'] = d['2039:Chennai(Mn)'] - d[
                        '2040:P2P(Mn)'] - d['2041:Outstation(Mn)']
            except:
                pass
            try:
                if d['2049:P2P(Mn)'] != 0 and d['2050:Outstation(Mn)'] != 0:
                    calc_dict['2051:Rental(Mn)'] = d['2048:Pune(Mn)'] - d[
                        '2049:P2P(Mn)'] - d['2050:Outstation(Mn)']
            except:
                pass
            try:
                calc_dict['2069:Rest of India(Mn)'] = d['1972:Cab Total(Mn)'] - (
                    d['2057:Lucknow(Mn)'] + d['2058:Jaipur(Mn)'] + d[
                    '2059:Chandigarh(Mn)'] + d['2060:Ahmedabad(Mn)'] + d[
                    '2061:Nagpur(Mn)'] + d['2062:Bhopal(Mn)'] + d[
                    '2063:Patna(Mn)'] + d['2064:Ranchi(Mn)'] + d[
                    '2065:Guwahati(Mn)'] + d['2066:Kanpur(Mn)'] + d[
                    '2067:Dehradun(Mn)'] + d['2068:Coimbatore(Mn)'] + d[
                    '1994:Delhi NCR(Mn)'] + d['2003:Mumbai(Mn)'] + d[
                    '2012:Bangalore(Mn)'] + d['2021:Kolkata(Mn)'] + d[
                    '2030:Hyderabad(Mn)'] + d['2039:Chennai(Mn)'] + d[
                    '2048:Pune(Mn)'])
            except:
                pass
            try:
                calc_dict['2083:Rest of India(Mn)'] = d['2070:Auto Total(Mn)'] - (
                    d['2071:Delhi NCR(Mn)'] + d['2072:Mumbai(Mn)'] + d[
                    '2073:Bangalore(Mn)'] + d['2074:Kolkata(Mn)'] + d[
                    '2075:Hyderabad(Mn)'] + d['2076:Chennai(Mn)'] + d[
                    '2077:Pune(Mn)'] + d['2078:Jaipur(Mn)'] + d[
                    '2079:Ahmedabad(Mn)'] + d['2080:Vijayawada(Mn)'] + d[
                    '2081:Tiruchirapalli(Mn)'] + d['2082:Indore(Mn)'])
            except:
                pass
            try:
                calc_dict['2114:Rest of India(Mn)'] = d['2084:Moto Total(Mn)'] - (
                    d['2085:Delhi NCR(Mn)'] + d['2086:Mumbai(Mn)'] + d[
                    '2087:Bangalore(Mn)'] + d['2088:Chennai(Mn)'] + d[
                    '2089:Hyderabad(Mn)'] + d['2090:Kolkata(Mn)'] + d[
                    '2091:Pune(Mn)'] + d['2092:Lucknow(Mn)'] + d[
                    '2093:Jaipur(Mn)'] + d['2094:Chandigarh(Mn)'] + d[
                    '2095:Ahmedabad(Mn)'] + d['2096:Bhopal(Mn)'] + d[
                    '2097:Patna(Mn)'] + d['2098:Ranchi(Mn)'] + d[
                    '2099:Guwahati(Mn)'] + d['2100:Kanpur(Mn)'] + d[
                    '2101:Coimbatore(Mn)'] + d['2102:Vijayawada(Mn)'] + d[
                    '2103:Tiruchirapalli(Mn)'] + d['2104:Bhubaneswar(Mn)'] + d[
                    '2105:Ludhiana(Mn)'] + d['2106:Indore(Mn)'] + d[
                    '2107:Visakhapatnam(Mn)'] + d['2108:Mysore(Mn)'] + d[
                    '2109:Madurai(Mn)'] + d['2110:Kota(Mn)'] + d[
                    '2111:Jodhpur(Mn)'] + d['2112:Guntur(Mn)'] + d[
                    '2113:Jalandhar(Mn)'])
            except:
                pass
            try:
                calc_dict['2115:Total(USD Mn)'] = d['2116:Cab Total(USD Mn)'] + d[
                    '2214:Auto Total(USD Mn)'] + d['2228:Moto Total(USD Mn)']
            except:
                pass
            try:
                calc_dict['2118:P2P(%)'] = d['2117:P2P(USD Mn)'] / d[
                    '2116:Cab Total(USD Mn)'] * 100
            except:
                pass
            try:
                calc_dict['2120:Outstation(%)'] = d['2119:Outstation(USD Mn)'] / d[
                    '2116:Cab Total(USD Mn)'] * 100
            except:
                pass
            try:
                calc_dict['2121:Rental(USD Mn)'] = d['2116:Cab Total(USD Mn)'] - d[
                    '2117:P2P(USD Mn)'] - d['2119:Outstation(USD Mn)']
            except:
                pass
            try:
                calc_dict['2122:Rental(%)'] = calc_dict['2121:Rental(USD Mn)'] / d[
                    '2116:Cab Total(USD Mn)'] * 100
            except:
                pass
            try:
                calc_dict['2124:Mini(%)'] = d['2123:Mini(USD Mn)'] / d[
                    '2116:Cab Total(USD Mn)'] * 100
            except:
                pass
            try:
                calc_dict['2126:Prime(%)'] = d['2125:Prime(USD Mn)'] / d[
                    '2116:Cab Total(USD Mn)'] * 100
            except:
                pass
            try:
                calc_dict['2128:Play(%)'] = d['2127:Play(USD Mn)'] / d[
                    '2116:Cab Total(USD Mn)'] * 100
            except:
                pass
            try:
                calc_dict['2129:SUV(USD Mn)'] = d['2116:Cab Total(USD Mn)'] - d[
                    '2123:Mini(USD Mn)'] - d['2125:Prime(USD Mn)'] - d[
                    '2127:Play(USD Mn)']
            except:
                pass
            try:
                calc_dict['2130:SUV(%)'] = calc_dict['2129:SUV(USD Mn)'] / d[
                    '2116:Cab Total(USD Mn)'] * 100
            except:
                pass
            try:
                calc_dict['2131:Top 7(USD Mn)'] = d['2138:Delhi NCR(USD Mn)'] + d[
                    '2147:Mumbai(USD Mn)'] + d['2156:Bangalore(USD Mn)'] + d[
                    '2165:Kolkata(USD Mn)'] + d['2174:Hyderabad(USD Mn)'] + d[
                    '2183:Chennai(USD Mn)'] + d['2192:Pune(USD Mn)']
            except:
                pass
            try:
                calc_dict['2132:Top 7(%)'] = calc_dict['2131:Top 7(USD Mn)'] / d[
                    '2116:Cab Total(USD Mn)'] * 100
            except:
                pass
            try:
                calc_dict['2133:Top 8-19(USD Mn)'] = d['2201:Lucknow(USD Mn)'] + d[
                    '2202:Jaipur(USD Mn)'] + d['2203:Chandigarh(USD Mn)'] + d[
                    '2204:Ahmedabad(USD Mn)'] + d['2205:Nagpur(USD Mn)'] + d[
                    '2206:Bhopal(USD Mn)'] + d['2207:Patna(USD Mn)'] + d[
                    '2208:Ranchi(USD Mn)'] + d['2209:Guwahati(USD Mn)'] + d[
                    '2210:Kanpur(USD Mn)'] + d['2211:Dehradun(USD Mn)'] + d[
                    '2212:Coimbatore(USD Mn)']
            except:
                pass
            try:
                calc_dict['2134:Top 8-19(%)'] = calc_dict['2133:Top 8-19(USD Mn)'
                    ] / d['2116:Cab Total(USD Mn)'] * 100
            except:
                pass
            try:
                if calc_dict['2131:Top 7(USD Mn)'] != 0 and calc_dict[
                    '2133:Top 8-19(USD Mn)'] != 0:
                    calc_dict['2135:Rest +19(USD Mn)'] = d['2116:Cab Total(USD Mn)'
                        ] - calc_dict['2131:Top 7(USD Mn)'] - calc_dict[
                        '2133:Top 8-19(USD Mn)']
            except:
                pass
            try:
                calc_dict['2136:Rest +19(%)'] = calc_dict['2135:Rest +19(USD Mn)'
                    ] / d['2116:Cab Total(USD Mn)'] * 100
            except:
                pass
            try:
                if d['2139:P2P(USD Mn)'] != 0 and d['2140:Outstation(USD Mn)'
                    ] != 0:
                    calc_dict['2141:Rental(USD Mn)'] = d['2138:Delhi NCR(USD Mn)'
                        ] - d['2139:P2P(USD Mn)'] - d['2140:Outstation(USD Mn)']
                if d['2148:P2P(USD Mn)'] != 0 and d['2149:Outstation(USD Mn)'
                    ] != 0:
                    calc_dict['2150:Rental(USD Mn)'] = d['2147:Mumbai(USD Mn)'
                        ] - d['2148:P2P(USD Mn)'] - d['2149:Outstation(USD Mn)']
                if d['2157:P2P(USD Mn)'] != 0 and d['2158:Outstation(USD Mn)'
                    ] != 0:
                    calc_dict['2159:Rental(USD Mn)'] = d['2156:Bangalore(USD Mn)'
                        ] - d['2157:P2P(USD Mn)'] - d['2158:Outstation(USD Mn)']
                if d['2166:P2P(USD Mn)'] != 0 and d['2167:Outstation(USD Mn)'
                    ] != 0:
                    calc_dict['2168:Rental(USD Mn)'] = d['2165:Kolkata(USD Mn)'
                        ] - d['2166:P2P(USD Mn)'] - d['2167:Outstation(USD Mn)']
                if d['2175:P2P(USD Mn)'] != 0 and d['2176:Outstation(USD Mn)'
                    ] != 0:
                    calc_dict['2177:Rental(USD Mn)'] = d['2174:Hyderabad(USD Mn)'
                        ] - d['2175:P2P(USD Mn)'] - d['2176:Outstation(USD Mn)']
                if d['2184:P2P(USD Mn)'] != 0 and d['2185:Outstation(USD Mn)'
                    ] != 0:
                    calc_dict['2186:Rental(USD Mn)'] = d['2183:Chennai(USD Mn)'
                        ] - d['2184:P2P(USD Mn)'] - d['2185:Outstation(USD Mn)']
                calc_dict['2146:SUV(%)'] = 100 - d['2143:Mini(%)'] - d[
                    '2144:Prime(%)'] - d['2145:Play(%)']
                if calc_dict['2146:SUV(%)'] == 100:
                    calc_dict['2146:SUV(%)'] = 0
                calc_dict['2155:SUV(%)'] = 100 - d['2152:Mini(%)'] - d[
                    '2153:Prime(%)'] - d['2154:Play(%)']
                if calc_dict['2155:SUV(%)'] == 100:
                    calc_dict['2155:SUV(%)'] = 0
                calc_dict['2164:SUV(%)'] = 100 - d['2161:Mini(%)'] - d[
                    '2162:Prime(%)'] - d['2163:Play(%)']
                if calc_dict['2164:SUV(%)'] == 100:
                    calc_dict['2164:SUV(%)'] = 0
                calc_dict['2173:SUV(%)'] = 100 - d['2170:Mini(%)'] - d[
                    '2171:Prime(%)'] - d['2172:Play(%)']
                if calc_dict['2173:SUV(%)'] == 100:
                    calc_dict['2173:SUV(%)'] = 0
                calc_dict['2182:SUV(%)'] = 100 - d['2179:Mini(%)'] - d[
                    '2180:Prime(%)'] - d['2181:Play(%)']
                if calc_dict['2182:SUV(%)'] == 100:
                    calc_dict['2182:SUV(%)'] = 0
                calc_dict['2191:SUV(%)'] = 100 - d['2188:Mini(%)'] - d[
                    '2189:Prime(%)'] - d['2190:Play(%)']
                if calc_dict['2191:SUV(%)'] == 100:
                    calc_dict['2191:SUV(%)'] = 0
                calc_dict['2200:SUV(%)'] = 100 - d['2197:Mini(%)'] - d[
                    '2198:Prime(%)'] - d['2199:Play(%)']
                if calc_dict['2200:SUV(%)'] == 100:
                    calc_dict['2200:SUV(%)'] = 0
                calc_dict['2213:Rest of India(USD Mn)'] = d[
                    '2116:Cab Total(USD Mn)'] - (d['2201:Lucknow(USD Mn)'] + d[
                    '2202:Jaipur(USD Mn)'] + d['2203:Chandigarh(USD Mn)'] + d[
                    '2204:Ahmedabad(USD Mn)'] + d['2205:Nagpur(USD Mn)'] + d[
                    '2206:Bhopal(USD Mn)'] + d['2207:Patna(USD Mn)'] + d[
                    '2208:Ranchi(USD Mn)'] + d['2209:Guwahati(USD Mn)'] + d[
                    '2210:Kanpur(USD Mn)'] + d['2211:Dehradun(USD Mn)'] + d[
                    '2212:Coimbatore(USD Mn)'] + d['2192:Pune(USD Mn)'] + d[
                    '2183:Chennai(USD Mn)'] + d['2174:Hyderabad(USD Mn)'] + d[
                    '2165:Kolkata(USD Mn)'] + d['2156:Bangalore(USD Mn)'] + d[
                    '2147:Mumbai(USD Mn)'] + d['2138:Delhi NCR(USD Mn)'])
                calc_dict['2227:Rest of India(USD Mn)'] = d[
                    '2214:Auto Total(USD Mn)'] - (d['2215:Delhi NCR(USD Mn)'] +
                    d['2216:Mumbai(USD Mn)'] + d['2217:Bangalore(USD Mn)'] + d[
                    '2218:Kolkata(USD Mn)'] + d['2219:Hyderabad(USD Mn)'] + d[
                    '2220:Chennai(USD Mn)'] + d['2221:Pune(USD Mn)'] + d[
                    '2222:Jaipur(USD Mn)'] + d['2223:Ahmedabad(USD Mn)'] + d[
                    '2224:Vijayawada(USD Mn)'] + d[
                    '2225:Tiruchirapalli(USD Mn)'] + d['2226:Indore(USD Mn)'])
                calc_dict['2258:Rest of India(USD Mn)'] = d[
                    '2228:Moto Total(USD Mn)'] - (d['2229:Delhi NCR(USD Mn)'] +
                    d['2230:Mumbai(USD Mn)'] + d['2231:Bangalore(USD Mn)'] + d[
                    '2232:Chennai(USD Mn)'] + d['2233:Hyderabad(USD Mn)'] + d[
                    '2234:Kolkata(USD Mn)'] + d['2235:Pune(USD Mn)'] + d[
                    '2236:Lucknow(USD Mn)'] + d['2237:Jaipur(USD Mn)'] + d[
                    '2238:Chandigarh(USD Mn)'] + d['2239:Ahmedabad(USD Mn)'] +
                    d['2240:Bhopal(USD Mn)'] + d['2241:Patna(USD Mn)'] + d[
                    '2242:Ranchi(USD Mn)'] + d['2243:Guwahati(USD Mn)'] + d[
                    '2244:Kanpur(USD Mn)'] + d['2245:Coimbatore(USD Mn)'] + d[
                    '2246:Vijayawada(USD Mn)'] + d[
                    '2247:Tiruchirapalli(USD Mn)'] + d[
                    '2248:Bhubaneswar(USD Mn)'] + d['2249:Ludhiana(USD Mn)'] +
                    d['2250:Indore(USD Mn)'] + d['2251:Visakhapatnam(USD Mn)'] +
                    d['2252:Mysore(USD Mn)'] + d['2253:Madurai(USD Mn)'] + d[
                    '2254:Kota(USD Mn)'] + d['2255:Jodhpur(USD Mn)'] + d[
                    '2256:Guntur(USD Mn)'] + d['2257:Jalandhar(USD Mn)'])
            except:
                pass
            try:
                calc_dict['2259:Total(USD)'] = calc_dict['2115:Total(USD Mn)'
                    ] / calc_dict['1971:Total(Mn)']
            except:
                pass
            try:
                calc_dict['2260:Cab Total(USD)'] = d['2116:Cab Total(USD Mn)'] / d[
                    '1972:Cab Total(Mn)']
            except:
                pass
            try:
                calc_dict['2261:P2P(USD)'] = d['2117:P2P(USD Mn)'] / calc_dict[
                    '1973:P2P(Mn)']
            except:
                pass
            try:
                calc_dict['2262:P2P(%)'] = calc_dict['2118:P2P(%)'] / d[
                    '1974:P2P(%)']
            except:
                pass
            try:
                calc_dict['2263:Outstation(USD)'] = d['2119:Outstation(USD Mn)'
                    ] / calc_dict['1975:Outstation(Mn)']
            except:
                pass
            try:
                calc_dict['2264:Outstation(%)'] = calc_dict['2120:Outstation(%)'
                    ] / d['1976:Outstation(%)']
            except:
                pass
            try:
                calc_dict['2265:Rental(USD)'] = calc_dict['2121:Rental(USD Mn)'
                    ] / calc_dict['1977:Rental(Mn)']
            except:
                pass
            try:
                calc_dict['2266:Rental(%)'] = calc_dict['2122:Rental(%)'
                    ] / calc_dict['1978:Rental(%)']
            except:
                pass
            try:
                calc_dict['2267:Mini(USD)'] = d['2123:Mini(USD Mn)'] / d[
                    '1979:Mini(Mn)']
            except:
                pass
            try:
                calc_dict['2268:Mini(%)'] = calc_dict['2124:Mini(%)'] / calc_dict[
                    '1980:Mini(%)']
            except:
                pass
            try:
                calc_dict['2269:Prime(USD)'] = d['2125:Prime(USD Mn)'] / d[
                    '1981:Prime(Mn)']
            except:
                pass
            try:
                calc_dict['2270:Prime(%)'] = calc_dict['2126:Prime(%)'
                    ] / calc_dict['1982:Prime(%)']
            except:
                pass
            try:
                calc_dict['2271:Play(USD)'] = d['2127:Play(USD Mn)'] / d[
                    '1983:Play(Mn)']
            except:
                pass
            try:
                calc_dict['2272:Play(%)'] = calc_dict['2128:Play(%)'] / calc_dict[
                    '1984:Play(%)']
            except:
                pass
            try:
                calc_dict['2273:SUV(USD)'] = calc_dict['2129:SUV(USD Mn)'
                    ] / calc_dict['1985:SUV(Mn)']
            except:
                pass
            try:
                calc_dict['2274:SUV(%)'] = calc_dict['2130:SUV(%)'] / calc_dict[
                    '1986:SUV(%)']
            except:
                pass
            try:
                calc_dict['2275:Top 7(USD)'] = calc_dict['2131:Top 7(USD Mn)'
                    ] / calc_dict['1987:Top 7(Mn)']
            except:
                pass
            try:
                calc_dict['2276:Top 7(%)'] = calc_dict['2132:Top 7(%)'
                    ] / calc_dict['1988:Top 7(%)']
            except:
                pass
            try:
                calc_dict['2277:Top 8-19(USD)'] = calc_dict['2133:Top 8-19(USD Mn)'
                    ] / calc_dict['1989:Top 8-19(Mn)']
            except:
                pass
            try:
                calc_dict['2278:Top 8-19(%)'] = calc_dict['2134:Top 8-19(%)'
                    ] / calc_dict['1990:Top 8-19(%)']
            except:
                pass
            try:
                calc_dict['2279:Rest +19(USD)'] = calc_dict['2135:Rest +19(USD Mn)'
                    ] / calc_dict['1991:Rest +19(Mn)']
            except:
                pass
            try:
                calc_dict['2280:Rest +19(%)'] = calc_dict['2136:Rest +19(%)'
                    ] / calc_dict['1992:Rest +19(%)']
            except:
                pass
            try:
                calc_dict['2281:Corporate(USD)'] = d['2137:Total Corporate(USD Mn)'
                    ] / d['1993:Total Corporate(Mn)']
            except:
                pass
            try:
                calc_dict['2282:Delhi NCR(USD)'] = d['2138:Delhi NCR(USD Mn)'] / d[
                    '1994:Delhi NCR(Mn)']
            except:
                pass
            try:
                calc_dict['2283:P2P(USD)'] = d['2139:P2P(USD Mn)'] / d[
                    '1995:P2P(Mn)']
            except:
                pass
            try:
                calc_dict['2284:Outstation(USD)'] = d['2140:Outstation(USD Mn)'
                    ] / d['1996:Outstation(Mn)']
            except:
                pass
            try:
                calc_dict['2285:Rental(USD)'] = calc_dict['2141:Rental(USD Mn)'
                    ] / calc_dict['1997:Rental(Mn)']
            except:
                pass
            try:
                calc_dict['2286:Corporate(USD)'] = d['2142:Delhi NCR(USD Mn)'] / d[
                    '1998:Delhi NCR(Mn)']
            except:
                pass
            try:
                calc_dict['2287:Mini(USD)'] = d['2138:Delhi NCR(USD Mn)'] * d[
                    '2143:Mini(%)'] / (d['1994:Delhi NCR(Mn)'] * d['1999:Mini(%)'])
            except:
                pass
            try:
                calc_dict['2288:Prime(USD)'] = d['2138:Delhi NCR(USD Mn)'] * d[
                    '2144:Prime(%)'] / (d['1994:Delhi NCR(Mn)'] * d[
                    '2000:Prime(%)'])
            except:
                pass
            try:
                calc_dict['2289:Play(USD)'] = d['2138:Delhi NCR(USD Mn)'] * d[
                    '2145:Play(%)'] / (d['1994:Delhi NCR(Mn)'] * d['2001:Play(%)'])
            except:
                pass
            try:
                calc_dict['2290:SUV(USD)'] = d['2138:Delhi NCR(USD Mn)'
                    ] * calc_dict['2146:SUV(%)'] / (d['1994:Delhi NCR(Mn)'] *
                    calc_dict['2002:SUV(%)'])
            except:
                pass
            try:
                calc_dict['2291:Mumbai(USD)'] = d['2147:Mumbai(USD Mn)'] / d[
                    '2003:Mumbai(Mn)']
            except:
                pass
            try:
                calc_dict['2292:P2P(USD)'] = d['2148:P2P(USD Mn)'] / d[
                    '2004:P2P(Mn)']
            except:
                pass
            try:
                calc_dict['2293:Outstation(USD)'] = d['2149:Outstation(USD Mn)'
                    ] / d['2005:Outstation(Mn)']
            except:
                pass
            try:
                calc_dict['2294:Rental(USD)'] = calc_dict['2150:Rental(USD Mn)'
                    ] / calc_dict['2006:Rental(Mn)']
            except:
                pass
            try:
                calc_dict['2295:Corporate(USD)'] = d['2151:Mumbai(USD Mn)'] / d[
                    '2007:Mumbai(Mn)']
            except:
                pass
            try:
                calc_dict['2296:Mini(USD)'] = d['2147:Mumbai(USD Mn)'] * d[
                    '2152:Mini(%)'] / (d['2003:Mumbai(Mn)'] * d['2008:Mini(%)'])
            except:
                pass
            try:
                calc_dict['2297:Prime(USD)'] = d['2147:Mumbai(USD Mn)'] * d[
                    '2153:Prime(%)'] / (d['2003:Mumbai(Mn)'] * d['2009:Prime(%)'])
            except:
                pass
            try:
                calc_dict['2298:Play(USD)'] = d['2147:Mumbai(USD Mn)'] * d[
                    '2154:Play(%)'] / (d['2003:Mumbai(Mn)'] * d['2010:Play(%)'])
            except:
                pass
            try:
                calc_dict['2299:SUV(USD)'] = d['2147:Mumbai(USD Mn)'] * calc_dict[
                    '2155:SUV(%)'] / (d['2003:Mumbai(Mn)'] * calc_dict[
                    '2011:SUV(%)'])
            except:
                pass
            try:
                calc_dict['2300:Bangalore(USD)'] = d['2156:Bangalore(USD Mn)'] / d[
                    '2012:Bangalore(Mn)']
            except:
                pass
            try:
                calc_dict['2301:P2P(USD)'] = d['2157:P2P(USD Mn)'] / d[
                    '2013:P2P(Mn)']
            except:
                pass
            try:
                calc_dict['2302:Outstation(USD)'] = d['2158:Outstation(USD Mn)'
                    ] / d['2014:Outstation(Mn)']
            except:
                pass
            try:
                calc_dict['2303:Rental(USD)'] = calc_dict['2159:Rental(USD Mn)'
                    ] / calc_dict['2015:Rental(Mn)']
            except:
                pass
            try:
                calc_dict['2304:Corporate(USD)'] = d['2160:Bangalore(USD Mn)'] / d[
                    '2016:Bangalore(Mn)']
            except:
                pass
            try:
                calc_dict['2305:Mini(USD)'] = d['2156:Bangalore(USD Mn)'] * d[
                    '2161:Mini(%)'] / (d['2012:Bangalore(Mn)'] * d['2017:Mini(%)'])
            except:
                pass
            try:
                calc_dict['2306:Prime(USD)'] = d['2156:Bangalore(USD Mn)'] * d[
                    '2162:Prime(%)'] / (d['2012:Bangalore(Mn)'] * d[
                    '2018:Prime(%)'])
            except:
                pass
            try:
                calc_dict['2307:Play(USD)'] = d['2156:Bangalore(USD Mn)'] * d[
                    '2163:Play(%)'] / (d['2012:Bangalore(Mn)'] * d['2019:Play(%)'])
            except:
                pass
            try:
                calc_dict['2308:SUV(USD)'] = d['2156:Bangalore(USD Mn)'
                    ] * calc_dict['2164:SUV(%)'] / (d['2012:Bangalore(Mn)'] *
                    calc_dict['2020:SUV(%)'])
            except:
                pass
            try:
                calc_dict['2309:Kolkata(USD)'] = d['2165:Kolkata(USD Mn)'] / d[
                    '2021:Kolkata(Mn)']
            except:
                pass
            try:
                calc_dict['2310:P2P(USD)'] = d['2166:P2P(USD Mn)'] / d[
                    '2022:P2P(Mn)']
            except:
                pass
            try:
                calc_dict['2311:Outstation(USD)'] = d['2167:Outstation(USD Mn)'
                    ] / d['2023:Outstation(Mn)']
            except:
                pass
            try:
                calc_dict['2312:Rental(USD)'] = calc_dict['2168:Rental(USD Mn)'
                    ] / calc_dict['2024:Rental(Mn)']
            except:
                pass
            try:
                calc_dict['2313:Corporate(USD)'] = d['2169:Kolkata(USD Mn)'] / d[
                    '2025:Kolkata(Mn)']
            except:
                pass
            try:
                calc_dict['2314:Mini(USD)'] = d['2165:Kolkata(USD Mn)'] * d[
                    '2170:Mini(%)'] / (d['2021:Kolkata(Mn)'] * d['2026:Mini(%)'])
            except:
                pass
            try:
                calc_dict['2315:Prime(USD)'] = d['2165:Kolkata(USD Mn)'] * d[
                    '2171:Prime(%)'] / (d['2021:Kolkata(Mn)'] * d['2027:Prime(%)'])
            except:
                pass
            try:
                calc_dict['2316:Play(USD)'] = d['2165:Kolkata(USD Mn)'] * d[
                    '2172:Play(%)'] / (d['2021:Kolkata(Mn)'] * d['2028:Play(%)'])
            except:
                pass
            try:
                calc_dict['2317:SUV(USD)'] = d['2165:Kolkata(USD Mn)'] * calc_dict[
                    '2173:SUV(%)'] / (d['2021:Kolkata(Mn)'] * calc_dict[
                    '2029:SUV(%)'])
            except:
                pass
            try:
                calc_dict['2318:Hyderabad(USD)'] = d['2174:Hyderabad(USD Mn)'] / d[
                    '2030:Hyderabad(Mn)']
            except:
                pass
            try:
                calc_dict['2319:P2P(USD)'] = d['2175:P2P(USD Mn)'] / d[
                    '2031:P2P(Mn)']
            except:
                pass
            try:
                calc_dict['2320:Outstation(USD)'] = d['2176:Outstation(USD Mn)'
                    ] / d['2032:Outstation(Mn)']
            except:
                pass
            try:
                calc_dict['2321:Rental(USD)'] = calc_dict['2177:Rental(USD Mn)'
                    ] / calc_dict['2033:Rental(Mn)']
            except:
                pass
            try:
                calc_dict['2322:Corporate(USD)'] = d['2178:Hyderabad(USD Mn)'] / d[
                    '2034:Hyderabad(Mn)']
            except:
                pass
            try:
                calc_dict['2323:Mini(USD)'] = d['2174:Hyderabad(USD Mn)'] * d[
                    '2179:Mini(%)'] / (d['2030:Hyderabad(Mn)'] * d['2035:Mini(%)'])
            except:
                pass
            try:
                calc_dict['2324:Prime(USD)'] = d['2174:Hyderabad(USD Mn)'] * d[
                    '2180:Prime(%)'] / (d['2030:Hyderabad(Mn)'] * d[
                    '2036:Prime(%)'])
            except:
                pass
            try:
                calc_dict['2325:Play(USD)'] = d['2174:Hyderabad(USD Mn)'] * d[
                    '2181:Play(%)'] / (d['2030:Hyderabad(Mn)'] * d['2037:Play(%)'])
            except:
                pass
            try:
                calc_dict['2326:SUV(USD)'] = d['2174:Hyderabad(USD Mn)'
                    ] * calc_dict['2182:SUV(%)'] / (d['2030:Hyderabad(Mn)'] *
                    calc_dict['2038:SUV(%)'])
            except:
                pass
            try:
                calc_dict['2327:Chennai(USD)'] = d['2183:Chennai(USD Mn)'] / d[
                    '2039:Chennai(Mn)']
            except:
                pass
            try:
                calc_dict['2328:P2P(USD)'] = d['2184:P2P(USD Mn)'] / d[
                    '2040:P2P(Mn)']
            except:
                pass
            try:
                calc_dict['2329:Outstation(USD)'] = d['2185:Outstation(USD Mn)'
                    ] / d['2041:Outstation(Mn)']
            except:
                pass
            try:
                calc_dict['2330:Rental(USD)'] = calc_dict['2186:Rental(USD Mn)'
                    ] / calc_dict['2042:Rental(Mn)']
            except:
                pass
            try:
                calc_dict['2331:Corporate(USD)'] = d['2187:Chennai(USD Mn)'] / d[
                    '2043:Chennai(Mn)']
            except:
                pass
            try:
                calc_dict['2332:Mini(USD)'] = d['2183:Chennai(USD Mn)'] * d[
                    '2188:Mini(%)'] / (d['2039:Chennai(Mn)'] * d['2044:Mini(%)'])
            except:
                pass
            try:
                calc_dict['2333:Prime(USD)'] = d['2183:Chennai(USD Mn)'] * d[
                    '2189:Prime(%)'] / (d['2039:Chennai(Mn)'] * d['2045:Prime(%)'])
            except:
                pass
            try:
                calc_dict['2334:Play(USD)'] = d['2183:Chennai(USD Mn)'] * d[
                    '2190:Play(%)'] / (d['2039:Chennai(Mn)'] * d['2046:Play(%)'])
            except:
                pass
            try:
                calc_dict['2335:SUV(USD)'] = d['2183:Chennai(USD Mn)'] * calc_dict[
                    '2191:SUV(%)'] / (d['2039:Chennai(Mn)'] * calc_dict[
                    '2047:SUV(%)'])
            except:
                pass
            try:
                calc_dict['2336:Pune(USD)'] = d['2192:Pune(USD Mn)'] / d[
                    '2048:Pune(Mn)']
            except:
                pass
            try:
                calc_dict['2337:P2P(USD)'] = d['2193:P2P(USD Mn)'] / d[
                    '2049:P2P(Mn)']
            except:
                pass
            try:
                calc_dict['2338:Outstation(USD)'] = d['2194:Outstation(USD Mn)'
                    ] / d['2050:Outstation(Mn)']
            except:
                pass
            try:
                calc_dict['2339:Rental(USD)'] = d['2195:Rental(USD Mn)'
                    ] / calc_dict['2051:Rental(Mn)']
            except:
                pass
            try:
                calc_dict['2340:Corporate(USD)'] = d['2196:Pune(USD Mn)'] / d[
                    '2052:Pune(Mn)']
            except:
                pass
            try:
                calc_dict['2341:Mini(USD)'] = d['2192:Pune(USD Mn)'] * d[
                    '2197:Mini(%)'] / (d['2048:Pune(Mn)'] * d['2053:Mini(%)'])
            except:
                pass
            try:
                calc_dict['2342:Prime(USD)'] = d['2192:Pune(USD Mn)'] * d[
                    '2198:Prime(%)'] / (d['2048:Pune(Mn)'] * d['2054:Prime(%)'])
            except:
                pass
            try:
                calc_dict['2343:Play(USD)'] = d['2192:Pune(USD Mn)'] * d[
                    '2199:Play(%)'] / (d['2048:Pune(Mn)'] * d['2055:Play(%)'])
            except:
                pass
            try:
                calc_dict['2344:SUV(USD)'] = d['2192:Pune(USD Mn)'] * calc_dict[
                    '2200:SUV(%)'] / (d['2048:Pune(Mn)'] * calc_dict['2056:SUV(%)']
                    )
            except:
                pass
            try:
                calc_dict['2345:Lucknow(USD)'] = d['2201:Lucknow(USD Mn)'] / d[
                    '2057:Lucknow(Mn)']
            except:
                pass
            try:
                calc_dict['2346:Jaipur(USD)'] = d['2202:Jaipur(USD Mn)'] / d[
                    '2058:Jaipur(Mn)']
            except:
                pass
            try:
                calc_dict['2347:Chandigarh(USD)'] = d['2203:Chandigarh(USD Mn)'
                    ] / d['2059:Chandigarh(Mn)']
            except:
                pass
            try:
                calc_dict['2348:Ahmedabad(USD)'] = d['2204:Ahmedabad(USD Mn)'] / d[
                    '2060:Ahmedabad(Mn)']
            except:
                pass
            try:
                calc_dict['2349:Nagpur(USD)'] = d['2205:Nagpur(USD Mn)'] / d[
                    '2061:Nagpur(Mn)']
            except:
                pass
            try:
                calc_dict['2350:Bhopal(USD)'] = d['2206:Bhopal(USD Mn)'] / d[
                    '2062:Bhopal(Mn)']
            except:
                pass
            try:
                calc_dict['2351:Patna(USD)'] = d['2207:Patna(USD Mn)'] / d[
                    '2063:Patna(Mn)']
            except:
                pass
            try:
                calc_dict['2352:Ranchi(USD)'] = d['2208:Ranchi(USD Mn)'] / d[
                    '2064:Ranchi(Mn)']
            except:
                pass
            try:
                calc_dict['2353:Guwahati(USD)'] = d['2209:Guwahati(USD Mn)'] / d[
                    '2065:Guwahati(Mn)']
            except:
                pass
            try:
                calc_dict['2354:Kanpur(USD)'] = d['2210:Kanpur(USD Mn)'] / d[
                    '2066:Kanpur(Mn)']
            except:
                pass
            try:
                calc_dict['2355:Dehradun(USD)'] = d['2211:Dehradun(USD Mn)'] / d[
                    '2067:Dehradun(Mn)']
            except:
                pass
            try:
                calc_dict['2356:Coimbatore(USD)'] = d['2212:Coimbatore(USD Mn)'
                    ] / d['2068:Coimbatore(Mn)']
            except:
                pass
            try:
                calc_dict['2357:Rest of India(USD)'] = calc_dict[
                    '2213:Rest of India(USD Mn)'] / calc_dict[
                    '2069:Rest of India(Mn)']
            except:
                pass
            try:
                calc_dict['2358:Auto Total(USD)'] = d['2214:Auto Total(USD Mn)'
                    ] / d['2070:Auto Total(Mn)']
            except:
                pass
            try:
                calc_dict['2359:Delhi NCR(USD)'] = d['2215:Delhi NCR(USD Mn)'] / d[
                    '2071:Delhi NCR(Mn)']
            except:
                pass
            try:
                calc_dict['2360:Mumbai(USD)'] = d['2216:Mumbai(USD Mn)'] / d[
                    '2072:Mumbai(Mn)']
            except:
                pass
            try:
                calc_dict['2361:Bangalore(USD)'] = d['2217:Bangalore(USD Mn)'] / d[
                    '2073:Bangalore(Mn)']
            except:
                pass
            try:
                calc_dict['2362:Kolkata(USD)'] = d['2218:Kolkata(USD Mn)'] / d[
                    '2074:Kolkata(Mn)']
            except:
                pass
            try:
                calc_dict['2363:Hyderabad(USD)'] = d['2219:Hyderabad(USD Mn)'] / d[
                    '2075:Hyderabad(Mn)']
            except:
                pass
            try:
                calc_dict['2364:Chennai(USD)'] = d['2220:Chennai(USD Mn)'] / d[
                    '2076:Chennai(Mn)']
            except:
                pass
            try:
                calc_dict['2365:Pune(USD)'] = d['2221:Pune(USD Mn)'] / d[
                    '2077:Pune(Mn)']
            except:
                pass
            try:
                calc_dict['2366:Jaipur(USD)'] = d['2222:Jaipur(USD Mn)'] / d[
                    '2078:Jaipur(Mn)']
            except:
                pass
            try:
                calc_dict['2367:Ahmedabad(USD)'] = d['2223:Ahmedabad(USD Mn)'] / d[
                    '2079:Ahmedabad(Mn)']
            except:
                pass
            try:
                calc_dict['2368:Vijayawada(USD)'] = d['2224:Vijayawada(USD Mn)'
                    ] / d['2080:Vijayawada(Mn)']
            except:
                pass
            try:
                calc_dict['2369:Tiruchirapalli(USD)'] = d[
                    '2225:Tiruchirapalli(USD Mn)'] / d['2081:Tiruchirapalli(Mn)']
            except:
                pass
            try:
                calc_dict['2370:Indore(USD)'] = d['2226:Indore(USD Mn)'] / d[
                    '2082:Indore(Mn)']
            except:
                pass
            try:
                calc_dict['2371:Rest of India(USD)'] = calc_dict[
                    '2227:Rest of India(USD Mn)'] / calc_dict[
                    '2083:Rest of India(Mn)']
            except:
                pass
            try:
                calc_dict['2372:Moto Total(USD)'] = d['2228:Moto Total(USD Mn)'
                    ] / d['2084:Moto Total(Mn)']
            except:
                pass
            try:
                calc_dict['2373:Delhi NCR(USD)'] = d['2229:Delhi NCR(USD Mn)'] / d[
                    '2085:Delhi NCR(Mn)']
            except:
                pass
            try:
                calc_dict['2374:Mumbai(USD)'] = d['2230:Mumbai(USD Mn)'] / d[
                    '2086:Mumbai(Mn)']
            except:
                pass
            try:
                calc_dict['2375:Bangalore(USD)'] = d['2231:Bangalore(USD Mn)'] / d[
                    '2087:Bangalore(Mn)']
            except:
                pass
            try:
                calc_dict['2376:Chennai(USD)'] = d['2232:Chennai(USD Mn)'] / d[
                    '2088:Chennai(Mn)']
            except:
                pass
            try:
                calc_dict['2377:Hyderabad(USD)'] = d['2233:Hyderabad(USD Mn)'] / d[
                    '2089:Hyderabad(Mn)']
            except:
                pass
            try:
                calc_dict['2378:Kolkata(USD)'] = d['2234:Kolkata(USD Mn)'] / d[
                    '2090:Kolkata(Mn)']
            except:
                pass
            try:
                calc_dict['2379:Pune(USD)'] = d['2235:Pune(USD Mn)'] / d[
                    '2091:Pune(Mn)']
            except:
                pass
            try:
                calc_dict['2380:Lucknow(USD)'] = d['2236:Lucknow(USD Mn)'] / d[
                    '2092:Lucknow(Mn)']
            except:
                pass
            try:
                calc_dict['2381:Jaipur(USD)'] = d['2237:Jaipur(USD Mn)'] / d[
                    '2093:Jaipur(Mn)']
            except:
                pass
            try:
                calc_dict['2382:Chandigarh(USD)'] = d['2238:Chandigarh(USD Mn)'
                    ] / d['2094:Chandigarh(Mn)']
            except:
                pass
            try:
                calc_dict['2383:Ahmedabad(USD)'] = d['2239:Ahmedabad(USD Mn)'] / d[
                    '2095:Ahmedabad(Mn)']
            except:
                pass
            try:
                calc_dict['2384:Bhopal(USD)'] = d['2240:Bhopal(USD Mn)'] / d[
                    '2096:Bhopal(Mn)']
            except:
                pass
            try:
                calc_dict['2385:Patna(USD)'] = d['2241:Patna(USD Mn)'] / d[
                    '2097:Patna(Mn)']
            except:
                pass
            try:
                calc_dict['2386:Ranchi(USD)'] = d['2242:Ranchi(USD Mn)'] / d[
                    '2098:Ranchi(Mn)']
            except:
                pass
            try:
                calc_dict['2387:Guwahati(USD)'] = d['2243:Guwahati(USD Mn)'] / d[
                    '2099:Guwahati(Mn)']
            except:
                pass
            try:
                calc_dict['2388:Kanpur(USD)'] = d['2244:Kanpur(USD Mn)'] / d[
                    '2100:Kanpur(Mn)']
            except:
                pass
            try:
                calc_dict['2389:Coimbatore(USD)'] = d['2245:Coimbatore(USD Mn)'
                    ] / d['2101:Coimbatore(Mn)']
            except:
                pass
            try:
                calc_dict['2390:Vijayawada(USD)'] = d['2246:Vijayawada(USD Mn)'
                    ] / d['2102:Vijayawada(Mn)']
            except:
                pass
            try:
                calc_dict['2391:Tiruchirapalli(USD)'] = d[
                    '2247:Tiruchirapalli(USD Mn)'] / d['2103:Tiruchirapalli(Mn)']
            except:
                pass
            try:
                calc_dict['2392:Bhubaneswar(USD)'] = d['2248:Bhubaneswar(USD Mn)'
                    ] / d['2104:Bhubaneswar(Mn)']
            except:
                pass
            try:
                calc_dict['2393:Ludhiana(USD)'] = d['2249:Ludhiana(USD Mn)'] / d[
                    '2105:Ludhiana(Mn)']
            except:
                pass
            try:
                calc_dict['2394:Indore(USD)'] = d['2250:Indore(USD Mn)'] / d[
                    '2106:Indore(Mn)']
            except:
                pass
            try:
                calc_dict['2395:Visakhapatnam(USD)'] = d[
                    '2251:Visakhapatnam(USD Mn)'] / d['2107:Visakhapatnam(Mn)']
            except:
                pass
            try:
                calc_dict['2396:Mysore(USD)'] = d['2252:Mysore(USD Mn)'] / d[
                    '2108:Mysore(Mn)']
            except:
                pass
            try:
                calc_dict['2397:Madurai(USD)'] = d['2253:Madurai(USD Mn)'] / d[
                    '2109:Madurai(Mn)']
            except:
                pass
            try:
                calc_dict['2398:Kota(USD)'] = d['2254:Kota(USD Mn)'] / d[
                    '2110:Kota(Mn)']
            except:
                pass
            try:
                calc_dict['2399:Jodhpur(USD)'] = d['2255:Jodhpur(USD Mn)'] / d[
                    '2111:Jodhpur(Mn)']
            except:
                pass
            try:
                calc_dict['2400:Guntur(USD)'] = d['2256:Guntur(USD Mn)'] / d[
                    '2112:Guntur(Mn)']
            except:
                pass
            try:
                calc_dict['2401:Jalandhar(USD)'] = d['2257:Jalandhar(USD Mn)'] / d[
                    '2113:Jalandhar(Mn)']
            except:
                pass
            try:
                calc_dict['2402:Rest of India(USD)'] = calc_dict[
                    '2258:Rest of India(USD Mn)'] / calc_dict[
                    '2114:Rest of India(Mn)']
            except:
                pass
            try:
                calc_dict['3675:P2P(Mn)'] = calc_dict['1973:P2P(Mn)'] - (d[
                    '1995:P2P(Mn)'] + d['2004:P2P(Mn)'] + d['2013:P2P(Mn)'] + d
                    ['2022:P2P(Mn)'] + d['2031:P2P(Mn)'] + d['2040:P2P(Mn)'] +
                    d['2049:P2P(Mn)'])
            except:
                pass
            try:
                calc_dict['3676:Outstation(Mn)'] = d['1975:Outstation(Mn)'] - (
                    d['1996:Outstation(Mn)'] + d['2005:Outstation(Mn)'] + d[
                    '2014:Outstation(Mn)'] + d['2023:Outstation(Mn)'] + d[
                    '2032:Outstation(Mn)'] + d['2041:Outstation(Mn)'] + d[
                    '2050:Outstation(Mn)'])
            except:
                pass
            try:
                calc_dict['3677:Rental(Mn)'] = d['1977:Rental(Mn)'] - (d[
                    '1997:Rental(Mn)'] + d['2006:Rental(Mn)'] + d[
                    '2015:Rental(Mn)'] + d['2024:Rental(Mn)'] + d[
                    '2033:Rental(Mn)'] + d['2042:Rental(Mn)'] + d[
                    '2051:Rental(Mn)'])
            except:
                pass
            try:
                calc_dict['3678:P2P(USD Mn)'] = d['2117:P2P(USD Mn)'] - (d[
                    '2139:P2P(USD Mn)'] + d['2148:P2P(USD Mn)'] + d[
                    '2157:P2P(USD Mn)'] + d['2166:P2P(USD Mn)'] + d[
                    '2175:P2P(USD Mn)'] + d['2184:P2P(USD Mn)'] + d[
                    '2193:P2P(USD Mn)'])
            except:
                pass
            try:
                calc_dict['3679:Outstation(USD Mn)'] = d['2119:Outstation(USD Mn)'
                    ] - (d['2140:Outstation(USD Mn)'] + d[
                    '2149:Outstation(USD Mn)'] + d['2158:Outstation(USD Mn)'] +
                    d['2167:Outstation(USD Mn)'] + d['2176:Outstation(USD Mn)'] +
                    d['2185:Outstation(USD Mn)'] + d['2194:Outstation(USD Mn)'])
            except:
                pass
            try:
                calc_dict['3680:Rental(USD Mn)'] = d['2121:Rental(USD Mn)'] - (
                    d['2141:Rental(USD Mn)'] + d['2150:Rental(USD Mn)'] + d[
                    '2159:Rental(USD Mn)'] + d['2168:Rental(USD Mn)'] + d[
                    '2177:Rental(USD Mn)'] + d['2186:Rental(USD Mn)'] + d[
                    '2195:Rental(USD Mn)'])
            except:
                pass
            data_tuples = []
            for k in calc_dict:
                if not calc_dict[k]:
                    continue
                parameter_id, parameter_name = k.split(':')
                parameter_id = int(parameter_id)
                data_dict = {'player_id': pl_id, 'start_date': str(sd),
                    'end_date': str(ed), 'parameter_id': parameter_id, 'value':
                    calc_dict[k], 'date_created': str(date.today()), 'source':
                    'webforms_calc', 'parametertree_id': 52, 'report_version_id': rep_ver_id}
                data_tuples.append(tuple(data_dict.values()))
            self.InsertORUpdate(data_tuples)
            WA_input_df = self.get_WA_sheet('Mobility')
            self.WA_Calc(pl_id, WA_input_df, sd, ed, db, rep_ver_id)
            d = self.par_val_dict(pl_id, sd, ed, db, id_name_dict)
            calc_dict = {}
            try:
                calc_dict['3681:Mini(Mn)'] = d['1979:Mini(Mn)'] - (d[
                    '3263:Mini'] + d['3267:Mini'] + d['3271:Mini'] + d[
                    '3275:Mini'] + d['3279:Mini'] + d['3283:Mini'] + d['3287:Mini']
                    )
            except:
                pass
            try:
                calc_dict['3682:Prime(Mn)'] = d['1981:Prime(Mn)'] - (d[
                    '3264:Prime'] + d['3268:Prime'] + d['3272:Prime'] + d[
                    '3276:Prime'] + d['3280:Prime'] + d['3284:Prime'] + d[
                    '3288:Prime'])
            except:
                pass
            try:
                calc_dict['3683:Play(Mn)'] = d['1983:Play(Mn)'] - (d[
                    '3265:Play'] + d['3269:Play'] + d['3273:Play'] + d[
                    '3277:Play'] + d['3281:Play'] + d['3285:Play'] + d['3289:Play']
                    )
            except:
                pass
            try:
                calc_dict['3684:SUV(Mn)'] = d['1985:SUV(Mn)'] - (d['3266:SUV'] +
                    d['3270:SUV'] + d['3274:SUV'] + d['3278:SUV'] + d[
                    '3282:SUV'] + d['3286:SUV'] + d['3290:SUV'])
            except:
                pass
            try:
                calc_dict['3685:Mini(USD Mn)'] = d['2123:Mini(USD Mn)'] - (d[
                    '3291:Mini'] + d['3295:Mini'] + d['3299:Mini'] + d[
                    '3303:Mini'] + d['3307:Mini'] + d['3311:Mini'] + d['3315:Mini']
                    )
            except:
                pass
            try:
                calc_dict['3686:Prime(USD Mn)'] = d['2125:Prime(USD Mn)'] - (d[
                    '3292:Prime'] + d['3296:Prime'] + d['3300:Prime'] + d[
                    '3304:Prime'] + d['3308:Prime'] + d['3312:Prime'] + d[
                    '3316:Prime'])
            except:
                pass
            try:
                calc_dict['3687:Play(USD Mn)'] = d['2127:Play(USD Mn)'] - (d[
                    '3293:Play'] + d['3297:Play'] + d['3301:Play'] + d[
                    '3305:Play'] + d['3309:Play'] + d['3313:Play'] + d['3317:Play']
                    )
            except:
                pass
            try:
                calc_dict['3688:SUV(USD Mn)'] = d['2129:SUV(USD Mn)'] - (d[
                    '3294:SUV'] + d['3298:SUV'] + d['3302:SUV'] + d['3306:SUV'] +
                    d['3310:SUV'] + d['3314:SUV'] + d['3318:SUV'])
            except:
                pass
            try:
                calc_dict['3673:Rest of India(USD Mn)'] = d[
                    '2137:Total Corporate(USD Mn)'] - (d[
                    '2142:Delhi NCR(USD Mn)'] + d['2151:Mumbai(USD Mn)'] + d[
                    '2160:Bangalore(USD Mn)'] + d['2169:Kolkata(USD Mn)'] + d[
                    '2178:Hyderabad(USD Mn)'] + d['2187:Chennai(USD Mn)'] + d[
                    '2196:Pune(USD Mn)'])
            except:
                pass
            try:
                calc_dict['3672:Rest of India(Mn)'] = d['1993:Total Corporate(Mn)'
                    ] - (d['1998:Delhi NCR(Mn)'] + d['2007:Mumbai(Mn)'] + d[
                    '2016:Bangalore(Mn)'] + d['2025:Kolkata(Mn)'] + d[
                    '2034:Hyderabad(Mn)'] + d['2043:Chennai(Mn)'] + d[
                    '2052:Pune(Mn)'])
            except:
                pass
            try:
                calc_dict['3674:Corporate(USD)'] = calc_dict[
                    '3673:Rest of India(USD Mn)'] / calc_dict[
                    '3672:Rest of India(Mn)']
            except:
                pass
            data_tuples = []
            for k in calc_dict:
                if not calc_dict[k]:
                    continue
                parameter_id, parameter_name = k.split(':')
                parameter_id = int(parameter_id)
                data_dict = {'player_id': pl_id, 'start_date': str(sd),
                    'end_date': str(ed), 'parameter_id': parameter_id, 'value':
                    calc_dict[k], 'date_created': str(date.today()), 'source':
                    'webforms_calc', 'parametertree_id': 52, 'report_version_id': rep_ver_id}
                data_tuples.append(tuple(data_dict.values()))
            self.InsertORUpdate(data_tuples)
            print('Mobility Script:- calc_script finished')
        except Exception as e:
            print('Mobility Script:- Error in calc_script:- ', e)


    def report_version_id(self, rep_ver_id, callback):
        print("Mobility Script:- calculate prapameter script started for report_version_id=", rep_ver_id)
        try:
            db = pymysql.connect(
                host=db_settings['HOST'],
                port=int(db_settings['PORT']),
                user=db_settings['USER'],
                password=db_settings['PASSWORD'],
                db=db_settings['NAME'],
                ssl={'ssl': {'tls': True}}
            )
            cur = db.cursor()
            cur.execute('select parameter_id, parameter_name from parameter;')
            parameters = cur.fetchall()
            param_df = pd.DataFrame.from_dict(parameters)
            param_df.rename(columns={(0): 'parameter_id', (1): 'parameter_name'},
                            inplace=True)
            param_id = param_df['parameter_id'].to_list()
            param_names = param_df['parameter_name'].to_list()
            id_name_dict = {}
            for i in range(len(param_id)):
                id_name_dict[param_id[i]] = ':'.join([str(param_id[i]), str(
                    param_names[i])])
            cur.close()
            cur = db.cursor()
            query = 'SELECT * FROM main_data where report_version_id = ' + str(
                rep_ver_id) + ';'
            cur.execute(query)
            data = cur.fetchall()
            data_df = pd.DataFrame.from_dict(data)
            data_df.rename(columns={(1): 'player_id', (2): 'start_date', (3):
                                    'end_date', (4): 'parameter_id', (5): 'value'}, inplace=True)
            player_id = data_df['player_id'].unique()[0]
            sd = str(data_df['start_date'].unique()[0])
            ed = str(data_df['end_date'].unique()[0])
            cur.close()
            self.calc_script(player_id, sd, ed, db, id_name_dict, rep_ver_id)
            WA_input_df = self.get_WA_sheet('Mobility')
            self.WA_Calc(player_id, WA_input_df, sd, ed, db, rep_ver_id)
            print("Mobility Script:- report_version_id finished")
            callback()
        except Exception as e:
            print("Mobility Script:- Error in report_version_id:- ", e)





