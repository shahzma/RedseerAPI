#%%
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
import sys
from django.conf import settings

db_settings = settings.DATABASES['default']

#%%

# change address in cursor
class CalculatedParamShotformFn:
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
        try:
            yr = int(sd[:4])
            month = int(sd[5:7])
            Total_number_days = calendar.monthrange(yr, month)[1]
            return Total_number_days
        except Exception as e:
            print(f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")}  Error:Month Range :-',e)
    @staticmethod
    def pr_sd(sd):#previous start date calculation
        try:
            year, month, day = sd.year, sd.month, sd.day
            if month == 1:
                return date(year - 1, 12, day)
            else:
                return date(year, month - 1, day)
        except Exception as e:
            print(f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")}  Error:Previous Start Date :-',e)


    @staticmethod
    def pr_ed(ed):#previous end date calculation
        try:
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
        except Exception as e:
            print(f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")}  Error:Previous End Date :-',e)

        
    @staticmethod
    def InsertORUpdate(dff,db):
        cur = db.cursor()
        try:
            value_list=[tuple(df.values()) for df in dff]
            query = """
            INSERT INTO main_data (
                player_id, start_date, end_date, parameter_id, value, date_created, source, parametertree_id, report_version_id
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) as value_list
            ON DUPLICATE KEY UPDATE value = VALUES(value), date_created = VALUES(date_created), report_version_id=VALUES(report_version_id)
            """
            cur.executemany(query, value_list)
            db.commit()
            print("Done")
            cur.close()
        except Exception as e:
            print(f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")}  Error:InsertOrUpdate :-',e)

    @staticmethod
    def par_val_dict(pl_id, sd, ed,db):
        try:
            
            cur = db.cursor()
            get_max_par = f"select max(parameter_id) from parameter;"
            cur.execute(get_max_par)
            max_par = cur.fetchall()
            max_par = int(max_par[0][0]) + 1
            print(max_par)


            
            cur.execute('select parameter_id, parameter_name from parameter;')
            parameters = cur.fetchall()
            param_df = pd.DataFrame.from_dict(parameters)
            param_df.rename(columns={(0): 'parameter_id', (1): 'parameter_name'},
                            inplace=True)
            param_id = param_df['parameter_id'].to_list()
            param_names = param_df['parameter_name'].to_list()
            id_name_dict = {}
            for i in range(len(param_id)):
                id_name_dict[param_id[i]] = ':'.join([str(param_id[i]), str(param_names[i])])
            s = "select * from main_data where player_id='" + str(pl_id) + "' and start_date='" + str(sd) + "' and end_date='" + str(ed) + "';"
            cur.execute(s)
            d = cur.fetchall()
            cur.close()
            dat = pd.DataFrame.from_dict(d)
            dat = dat[[4, 5]]
            # date=date.drop_duplicates(subset={2,3})
            dat = dat.rename(columns={4: 'par_id', 5: 'val'})
            ans = zip(dat.par_id, dat.val)
            ans = dict(ans)
            input_dict = {}
            print(ans)
            for i in id_name_dict:
                try:
                    ans[i]
                    input_dict[id_name_dict[i]]=ans[i]
                except:
                    input_dict[id_name_dict[i]] = None
            return input_dict
        except Exception as e:
            print(f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")}  Error:Par Val Dict :-',e)

    
    
    def upload_resumable2(self):
        try:
            # Creating a public client app, Aquire an access token for the user and set the header for API calls
            cognos_to_onedrive = msal.PublicClientApplication(self.CLIENT_ID, authority=self.AUTHORITY_URL)
            token = cognos_to_onedrive.acquire_token_by_username_password(self.USERNAME,self.PASSWORD,self.SCOPES)
            header = {'Authorization': 'Bearer {}'.format(token['access_token'])}
            # download 
            response = requests.get('{}/{}/me/drive/root:/Product Data Excels (Do not Touch)/Calculated_parameter_sheets'.format(self.RESOURCE_URL,self.API_VERSION) + '/' + self.file_name + ':/content', headers=header)

            return response.content
        except Exception as e:
            print(f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")}  Error:Upload Resumable :-',e)
    

    
    def WA_Calc(self,pl,sd,ed,rep_ver_id,db):
        try:
            yls=self.upload_resumable2()
            df=pd.read_excel(yls,"Shortform", header=None, index_col=False)
            required_df=[]
            dt=pd.Timestamp.today().date()
            dt=str(dt)
            cur=cur = db.cursor()

            print(df)
            print("player = ", pl)
            for k in range(1,len(df)):
                par_id=df.iloc[k,0]
                if str(par_id)=='nan':
                    continue 
                print(par_id)
                par1=df.iloc[k,4]
                par2=df.iloc[k,5]
                par3=df.iloc[k,6]
                A="SELECT value from main_data WHERE player_id= '"+str(pl)+"' AND start_date= '"+str(sd)+"'"+ \
                "AND parameter_id='"+str(par1)+"';"
                cur.execute(A)
                to=cur.fetchall()
                to=pd.DataFrame.from_dict(to)
                par_1=0
                par_2=0
                if len(to)!=0:
                    par_1=to.iat[0,0]
                if str(par2)=='no_days':
                    par_2=self.month_range(str(sd))
                else:
                    B="SELECT value from main_data WHERE player_id= '"+str(pl)+"' AND start_date= '"+str(sd)+"'"+ \
                    "AND parameter_id='"+str(par2)+"';"
                    cur.execute(B)
                    to=cur.fetchall()
                    to=pd.DataFrame.from_dict(to)
                    if len(to)!=0:
                        par_2=to.iat[0,0]
                if str(par3)=='nan':
                    val=par_1*par_2
                    print(par_id,par3)
                else:
                    val=par_1*par_2
                    val=val/100
                if val!=0:
                    print(val)
                    required_df.append({"player_id":pl,'start_date':sd,'end_date':ed,'parameter_id':par_id,'value':val,"date_created":dt,"source":'weight_avg','parametertree_id':52,'report_version_id':rep_ver_id})    
            print("\n"+"WA Insertion")
            self.InsertORUpdate(required_df, db)
            print(f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")}  Log:WA Ran Successfully for Shortform Player :-',pl)
            cur.close()
        except Exception as e:
            print(f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")}  Error:WA :-',e)

    
    def calc_script_shortform(self, pl_id, sd, ed,pr_sd,pr_ed,rep_ver_id,db):
        try:
            calc_dict = {}
            print(pl_id)
            try:
                d = self.par_val_dict(pl_id, sd, ed,db)
            except:
                pass

            try:
                d_pr = self.par_val_dict(pl_id, pr_sd, pr_ed,db)
            except:
                pass
            try:
                calc_dict["35:DAU/MAU (%)"]=(d["34:DAU (Mn)"]/d["52:MAU (Mn)"])*100
            except:
                pass
            try:
                calc_dict["64:Net MAU Addition (Mn)"]=d["52:MAU (Mn)"]-d_pr["52:MAU (Mn)"]
            except:
                pass
            try:
                calc_dict["24:Time Spent per DAU (Minutes)"]=d["8:# of sessions per DAU (#)"]*d["2:Time Spent per Session (Minute)"]
            except:
                pass
            try:
                calc_dict["128:Total Time Spent"]=calc_dict["24:Time Spent per DAU (Minutes)"]*d["34:DAU (Mn)"]*self.month_range(sd)
            except:
                pass
            
            try:
                calc_dict["110:Tier-2+ (%)"]=100-d["101:Metro (%)"]-d["103:Tier-1 (%)"]
            except:
                pass
            try:
                calc_dict["67:Others (%)"]=100-d["61:English (%)"]-d["63:Hindi (%)"]
            except:
                pass
            try:
                calc_dict["169:45+ yrs (%)"]=100-d["166:12-18 yrs (%)"]-d["167:18-30 yrs (%)"]-d["168:30-45 yrs (%)"]
            except:
                pass
            try:
                calc_dict["176:South (%)"]=100-d["175:North (%)"]-d["177:East (%)"]-d["178:West (%)"]
            except:
                pass
            try:
                calc_dict["181:T2 + (%)"]=100-d["179:Metro (%)"]-d["180:T1 (%)"]
            except:
                pass
            try:
                calc_dict["184:Others (%)"]=100-d["182:Others (%)"]-d["183:Hindi (%)"]
            except:
                pass
            try:
                calc_dict["189:45+ yrs (%)"]=100-d["186:12-18 yrs (%)"]-d["187:18-30 yrs (%)"]-d["188:30-45 yrs (%)"]
            except:
                pass
            try:
                calc_dict["196:South (%)"]=100-d["195:North (%)"]-d["197:East (%)"]-d["198:West (%)"]
            except:
                pass
            try:
                calc_dict["171:Phone (%)"]=d["172:iOS (%)"]+d["173:Android (%)"]
            except:
                pass
            try:
                calc_dict["174:Other Channel - ( Smart Devices, iPads, TVs. KaiOS, etc) (%)"]=100-d["170:Web (%)"]-calc_dict["171:Phone (%)"]
            except:
                pass
            try:
                calc_dict["191:Phone (%)"]=d["192:Android (%)"]+d["193:iOS (%)"]
            except:
                pass
            try:
                calc_dict["194:Other Channel (%)"]=100-d["190:Web (%)"]-calc_dict["191:Phone (%)"]
            except:
                pass
            try:
                calc_dict["3670:MAU/Registered User Base(%)"]=(d["52:MAU (Mn)"]/d["1844:Registered User Base(Mn)"])*100
            except:
                pass
            try:
                calc_dict["4261:Elite (Above 10Mn)"] = d["12:No of Users generating content (Mn)"] * d["4234:Elite (Above 10Mn)"]/100
            except:
                pass
            try:
                calc_dict["4262:Mega (500k-10Mn)"] = d["12:No of Users generating content (Mn)"] * d["4235:Mega (500k-10Mn)"]/100
            except:
                pass
            try:
                calc_dict["4263:Mini and Micro (10k-500)"] = d["12:No of Users generating content (Mn)"] * d["4236:Mini and Micro (10k-500)"]/100
            except:
                pass
            try:
                calc_dict["4786:Time Spent WA (Mn Min)"] = calc_dict["24:Time Spent per DAU (Minutes)"] * d["52:MAU (Mn)"]
            except:
                pass
            
            required_df=[]
            for k in calc_dict:
                if not calc_dict[k]:
                    continue
                parameter_id, parameter_name = k.split(':')
                parameter_id = int(parameter_id)
                required_df.append({"player_id":pl_id,'start_date':str(sd),'end_date':str(ed),'parameter_id':parameter_id,'value':calc_dict[k],"date_created": str(date.today()),"source":'webforms_calc','parametertree_id':52,"report_version_id":rep_ver_id})
            self.InsertORUpdate(required_df, db)
            print(f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")}  Log:Calc Script Ran Successfully for Shortform player -',pl_id)

        except Exception as e:
            print(f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")}  Error: Calc Script :-',e)

    def report_version_id(self, rep_ver_id, callback):
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
            query='select distinct player_id,start_date,end_date from main_data where report_version_id=(%s);'
            cur.execute(query,rep_ver_id)
            par = cur.fetchall()
            print(cur.fetchall())
            
            pl=par[0][0]
            sd=str(par[0][1])
            ed=str(par[0][2])
            p_sd=self.pr_sd(par[0][1])
            p_ed=self.pr_ed(par[0][2])
            print(p_sd)
            self.calc_script_shortform(pl,sd,ed,str(p_sd),str(p_ed),rep_ver_id,db)
            self.WA_Calc(pl,sd,ed,rep_ver_id,db)
            cur.close()
            db.close()
            print(f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Log: Shotform Script:- report_version_id finished')
            callback()
        except Exception as e:
            print(f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")}  Error:Report Version Id :-',e)

