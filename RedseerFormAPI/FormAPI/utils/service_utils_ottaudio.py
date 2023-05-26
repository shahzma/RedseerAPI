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

class CalculatedParamOTTAudioFn:
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
    def InsertORUpdate(dff):
        db = pymysql.connect(
            host=db_settings['HOST'],
            port=int(db_settings['PORT']),
            user=db_settings['USER'],
            password=db_settings['PASSWORD'],
            db=db_settings['NAME'],
            ssl={'ssl': {'tls': True}}
        )

        cur = db.cursor()
        try:
            value_list=[tuple(df.values()) for df in dff]
            query = """
            INSERT INTO main_data (
                player_id, start_date, end_date, parameter_id, value, date_created, source, parametertree_id, report_version_id
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) as value_list
            ON DUPLICATE KEY UPDATE value = VALUES(value), date_created = VALUES(date_created), report_version_id = VALUES(report_version_id)
            """
            cur.executemany(query, value_list)
            db.commit()
            print("Done")
            cur.close()
            db.close()
            print("OTTAudio Script:- InsertORUpdate finished")
        except Exception as e:
            print("OTTAudio Script:- Error in InsertORUpdate:- ", e)

    @staticmethod
    def par_val_dict(pl_id, sd, ed):
        db = pymysql.connect(
            host=db_settings['HOST'],
            port=int(db_settings['PORT']),
            user=db_settings['USER'],
            password=db_settings['PASSWORD'],
            db=db_settings['NAME'],
            ssl={'ssl': {'tls': True}}
        )
        get_max_par = f"select max(parameter_id) from parameter;"
        cur.execute(get_max_par)
        max_par = cur.fetchall()
        max_par = int(max_par[0][0]) + 1
        print(max_par)

        cur = db.cursor()
        s = "select * from main_data where player_id='" + str(pl_id) + "' and start_date='" + str(
            sd) + "' and end_date='" + str(ed) + "';"
        cur.execute(s)
        d = cur.fetchall()
        cur.close()
        dat = pd.DataFrame.from_dict(d)
        dat = dat[[4, 5]]
        # date=date.drop_duplicates(subset={2,3})
        dat = dat.rename(columns={4: 'par_id', 5: 'val'})
        ans = zip(dat.par_id, dat.val)
        ans = dict(ans)
        print(ans)
        for i in range(1, max_par):
            try:
                ans[i]
            except:
                ans[i] = None
        return ans
    
    @staticmethod
    def reset_calc_dict():
        calc_dict = {}
        for i in range(1, max_par):
            calc_dict[i] = None

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
    
    def upload_resumable2(self):
        # Creating a public client app, Aquire an access token for the user and set the header for API calls
        cognos_to_onedrive = msal.PublicClientApplication(self.CLIENT_ID, authority=self.AUTHORITY_URL)
        token = cognos_to_onedrive.acquire_token_by_username_password(self.USERNAME,self.PASSWORD,self.SCOPES)
        header = {'Authorization': 'Bearer {}'.format(token['access_token'])}
        # download 
        response = requests.get('{}/{}/me/drive/root:/Product Data Excels (Do not Touch)/Calculated_parameter_sheets'.format(self.RESOURCE_URL,self.API_VERSION) + '/' + self.file_name + ':/content', headers=header)

        return response.content



    # file_name = "Weighted Average Parameters - Benchmarks Sectors.xlsx"                     #data File name
    # #print(file_name)

    # conflict_resolve = {
    # "item": {
    #     "@microsoft.graph.conflictBehavior": "replace"
    # }
    # }
    

    
    def WA_Calc(self,pl,sd,ed,rep_ver_id):
        try:
            yls=self.upload_resumable2()
            df=pd.read_excel(yls,"OTT Audio", header=None, index_col=False)
            required_df=[]
            dt=pd.Timestamp.today().date()
            dt=str(dt)
            db = pymysql.connect(
                host=db_settings['HOST'],
                port=int(db_settings['PORT']),
                user=db_settings['USER'],
                password=db_settings['PASSWORD'],
                db=db_settings['NAME'],
                ssl={'ssl': {'tls': True}}
            )
            cur = db.cursor()

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
            self.InsertORUpdate(required_df)
            cur.close()
            db.close()
            print("OTTAudio Script:- WA_Calc finished")
        except Exception as e:
            print("OTTAudio Script:- Error in WA_Calc:- ", e)

    @staticmethod
    def OTTA(player,sd,ed):#market share
        try:
            li=[766,768,770,92,111,112,113,115,48,49,116]
            li2=[781,782,783,772,773,775,776,777,778,779,780]
            db = pymysql.connect(
                host=db_settings['HOST'],
                port=int(db_settings['PORT']),
                user=db_settings['USER'],
                password=db_settings['PASSWORD'],
                db=db_settings['NAME'],
                ssl={'ssl': {'tls': True}}
            )
            cur = db.cursor()
            for par in li2:
                c2=0
                print(par)
                v=0
                v2=0
                #par=li2[c]
                query ="SELECT SUM(value) FROM main_data WHERE player_id in (16,17,18,19,20,21,22,23) and start_date = (%s) and parameter_id=(%s);"
                value=(sd,par)
                #print(i[0])
                c1=cur.execute(query,value)
                if c1!=0:
                    v=list(cur.fetchall())
                    v=v[0][0]
                    print(v)
                else:
                    v=0

                
                print("player = ",player)
                query ="select value from main_data where player_id=(%s) and start_date=(%s) and parameter_id=(%s)"
                value=(player,sd,par)
                c1=cur.execute(query,value)
                if c1!=0:
                    v2=list(cur.fetchall())
                    v2=v2[0][0]
                    print(v2)
                else:
                    v2=0
                val=(v2/v)*100
                print(li[li2.index(par)]," = ",val)
                if val!=0:
                    a="SELECT * from main_data WHERE player_id= '"+str(player)+"' AND start_date= '"+str(sd)+"'" + \
                    " AND parameter_id="+ '"' + str(li[li2.index(par)]) +'";' 
                    print(a)
                    row_exist = cur.execute(a)
                    print(row_exist)
                    if row_exist==0:
                        query="insert into main_data(player_id,start_date,end_date,parameter_id,value,date_created,source,parametertree_id) values('"+str(player)+ "','"+str(sd)+"', '"+str(ed)+"','"+str(li[li2.index(par)])+"','"+str(val)+"', '"+str(date.today()) +"','"+'Benchmark_standz'+"','"+str(1)+"')"
                        print(query)
                        cur.execute(query)
                        db.commit()
                    else:
                        b="Update main_data set value='"+ str(val) +"' where player_id= '"+str(player)+"' AND start_date= '"+str(sd)+"'" +" AND parameter_id="+ '"' + str(li[li2.index(par)]) +'";'
                        print(b)
                        cur.execute(b)
                        db.commit()
            cur.close()
            db.close()
            print("OTTAudio Script:- OTTA finished")
        except Exception as e:
            print("OTTAudio Script:- Error in OTTA:- ", e)

    def calc_script_audio(self, pl_id, sd, ed,pr_sd,pr_ed,rep_ver_id):
        try:
            calc_dict = {}
            print(pl_id)
            try:
                d = self.par_val_dict(pl_id, sd, ed)
            except:
                pass
            try:
                d_pr = self.par_val_dict(pl_id, pr_sd, pr_ed)
            except:
                pass
            try:
                calc_dict[35]=(d[34]/d[52])*100
            except:
                pass
            try:
                calc_dict[64]=d[52]-d_pr[52]
            except:
                pass
            try:
                calc_dict[24]=d[8]*d[2]
            except:
                pass
            try:
                calc_dict[128]=calc_dict[24]*d[34]*self.month_range(sd)
            except:
                pass
            try:
                calc_dict[110]=100-d[101]-d[103]
            except:
                pass
            try:
                calc_dict[67]=100-d[61]-d[63]
            except:
                pass
            try:
                calc_dict[169]=100-d[166]-d[167]-d[168]
            except:
                pass
            try:
                calc_dict[176]=100-d[175]-d[177]-d[178]
            except:
                pass
            try:
                calc_dict[181]=100-d[179]-d[180]
            except:
                pass
            try:
                calc_dict[184]=100-d[182]-d[183]
            except:
                pass
            try:
                calc_dict[189]=100-d[186]-d[187]-d[188]
            except:
                pass
            try:
                calc_dict[196]=100-d[195]-d[197]-d[198]
            except:
                pass
            try:
                calc_dict[171]=d[172]+d[173]
            except:
                pass
            try:
                calc_dict[174]=100-d[170]-calc_dict[171]
            except:
                pass
            try:
                calc_dict[191]=d[192]+d[193]
            except:
                pass
            try:
                calc_dict[194]=100-d[190]-calc_dict[191]
            except:
                pass
            try:
                calc_dict[770]=100-d[766]-d[768]
            except:
                pass
            try:
                calc_dict[154]=100-d[153]-d[152]
            except:
                pass
            try:
                calc_dict[764]=100-(d[748]+d[750]+d[754]+d[756]+d[758]+d[760]+d[762])#updated 25/01/23
            except:
                pass
            try:
                calc_dict[93]=d[6]*d[22] #updated 11/01/22
            except:
                pass
            try:
                calc_dict[75]=d[18]+calc_dict[93]
            except:
                pass
            try:
                calc_dict[3670]=(d[52]/d[1844])*100
            except:
                pass
            try:
                calc_dict[4786] = calc_dict[24] * d[52]
            except:
                pass
            required_df=[]
            for k in calc_dict:
                if not calc_dict[k]:
                    continue
                required_df.append({"player_id":pl_id,'start_date':str(sd),'end_date':str(ed),'parameter_id':k,'value':calc_dict[k],"date_created": str(date.today()),"source":'webforms_calc','parametertree_id':52,'report_version_id':rep_ver_id})
            self.InsertORUpdate(required_df)
            print("OTTAudio Script:- calc_script_audio finished")
        except Exception as e:
            print("OTTAudio Script:- Error in calc_script_audio:- ", e)

    def report_version_id(self, rep_ver_id):
        print("OTTAudio Script:- calculate prapameter script started for report_version_id=", rep_ver_id)
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
            self.calc_script_audio(pl,sd,ed,str(p_sd),str(p_ed),rep_ver_id)
            self.WA_Calc(pl,sd,ed,rep_ver_id)
            self.OTTA(pl,sd,ed)
            cur.close()
            db.close()
            print("OTTAudio Script:- report_version_id finished")
        except Exception as e:
            print("OTTAudio Script:- Error in report_version_id:- ", e)






