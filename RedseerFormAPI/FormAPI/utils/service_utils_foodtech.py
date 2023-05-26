import pandas as pd
import os
import pymysql
import calendar
import requests
import datetime
from datetime import datetime
from datetime import date
import msal
from django.conf import settings
import sys

db_settings = settings.DATABASES['default']


class CalculatedParamFoodtechFn:
    def par_val_dict(self, pl_id, sd, ed, db, id_name_dict):
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
                    input_dict[id_name_dict[i]] = None
            print("Foodtech:- par_val_dict finished")
            return input_dict
        except Exception as e:
            print("Foodtech:- Error in par_val_dict:- ", e)

    def month_range(self, sd):
        try:
            yr = int(sd[:4])
            month = int(sd[5:7])
            Total_number_days = calendar.monthrange(yr, month)[1]
            # print("Foodtech:- month_range finished")
            return Total_number_days
        except Exception as e:
            print("Foodtech:- Error in month_range:- ", e)

    def InsertORUpdate(self, data, db):
        try:
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
            print("Foodtech:- InsertORUpdate finished")
        except Exception as e:
            print("Foodtech:- Error in InsertORUpdate:- ", e)

    def reset_calc_dict(self, id_name_dict):
        try:
            in_values = [None] * len(id_name_dict)
            calc_dict = dict(zip(list(id_name_dict.values()), in_values))
            print("Foodtech:- reset_calc_dict finished")
            return calc_dict
        except Exception as e:
            print("Foodtech:- Error in reset_calc_dict:- ", e)

    def upload_resumable2(self, file_name2):
        try:
            CLIENT_ID = 'fc1cef01-9962-458e-a314-4e31a3d10791'
            TENANT_ID = '00a9ff8c-9830-4847-ae51-4579ec092cb4'
            AUTHORITY_URL = (
                'https://login.microsoftonline.com/00a9ff8c-9830-4847-ae51-4579ec092cb4'
            )
            AUTHORITY_URL = 'https://login.microsoftonline.com/{}'.format(
                TENANT_ID)
            RESOURCE_URL = 'https://graph.microsoft.com/'
            API_VERSION = 'v1.0'
            USERNAME = 'operations@redseerconsulting.com'
            PASSWORD = 'BM@OPS@123'
            SCOPES = ['Sites.ReadWrite.All', 'Files.ReadWrite.All']
            cognos_to_onedrive = msal.PublicClientApplication(
                CLIENT_ID, authority=AUTHORITY_URL)
            token = cognos_to_onedrive.acquire_token_by_username_password(USERNAME,
                                                                          PASSWORD, SCOPES)
            header = {'Authorization': 'Bearer {}'.format(
                token['access_token'])}
            response = requests.get(
                '{}/{}/me/drive/root:/Product Data Excels (Do not Touch)/Calculated_parameter_sheets'
                .format(RESOURCE_URL, API_VERSION) + '/' + file_name2 + ':/content',
                headers=header)
            print("Foodtech:- upload_resumable2 finished")
            return response.content
        except Exception as e:
            print("Foodtech:- Error in upload_resumable2:- ", e)

    def get_WA_sheet(self, sheet_name):
        try:
            file_name2 = 'Weighted Average Parameters - Benchmarks Sectors.xlsx'
            conflict_resolve = {'item': {'@microsoft.graph.conflictBehavior':
                                         'replace'}}
            yls2 = self.upload_resumable2(file_name2)
            WA_input_df = pd.read_excel(
                yls2, sheet_name, header=None, index_col=False)
            print("Foodtech:- get_WA_sheet finished")
            return WA_input_df
        except Exception as e:
            print("Foodtech:- Error in get_WA_sheet:- ", e)

    def calc1(self, pl, sd, ed, db, rep_ver_id):
        try:
            cur = db.cursor()
            parameters_dict = {(417): 848, (1729): 849, (420): 850, (421): 851, (
                422): 852}
            required_rows = []
            AOV = "SELECT value from main_data WHERE player_id= '" + str(pl
                                                                         ) + "' AND start_date= '" + str(sd) + "'" + " AND end_date='" + str(ed
                                                                                                                                             ) + "'" + 'AND parameter_id=336'
            cur.execute(AOV)
            to = cur.fetchall()
            to = pd.DataFrame.from_dict(to)
            if len(to) != 0:
                aov = to.iat[0, 0]
            else:
                return 0
            MOV = aov * self.month_range(sd)
            for key, value in parameters_dict.items():
                par_in = key
                par_out = value
                rev = "SELECT value from main_data WHERE player_id= '" + str(pl) + "' AND start_date= '" + str(sd) + "'" + " AND end_date='" + str(ed
                                                                                                                                                   ) + "'" + "AND parameter_id='" + str(par_in) + "';"
                cur.execute(rev)
                to = cur.fetchall()
                to = pd.DataFrame.from_dict(to)
                if len(to) == 0:
                    continue
                rev1 = to.iat[0, 0]
                val = MOV * rev1 / 10000
                data_dict = {'player_id': pl, 'start_date': sd, 'end_date':
                             ed, 'parameter_id': par_out, 'value': val, 'date_created': str(date
                                                                                            .today()), 'source': 'Benchmarks', 'parametertree_id': 52, 'report_version_id': rep_ver_id}
                required_rows.append(tuple(data_dict.values()))
            cur.close()
            self.InsertORUpdate(required_rows, db)
            print("Foodtech:- calc1 finished")
        except Exception as e:
            print("Foodtech:- Error in calc1:- ", e)

    def calc2(self, pl, sd, ed, db, rep_ver_id):
        try:
            cur = db.cursor()
            parameters_dict = {(1727): 854, (1730): 855}
            required_rows = []
            AOV = "SELECT value from main_data WHERE player_id= '" + str(pl
                                                                         ) + "' AND start_date= '" + str(sd) + "'" + " AND end_date='" + str(ed
                                                                                                                                             ) + "'" + 'AND parameter_id=1720'
            cur.execute(AOV)
            to = cur.fetchall()
            to = pd.DataFrame.from_dict(to)
            if len(to) != 0:
                aov = to.iat[0, 0]
            for key, value in parameters_dict.items():
                par_in = key
                par_out = value
                rev = "SELECT value from main_data WHERE player_id= '" + str(pl
                                                                             ) + "' AND start_date= '" + str(sd
                                                                                                             ) + "'" + " AND end_date='" + str(ed
                                                                                                                                               ) + "'" + "AND parameter_id='" + str(par_in) + "';"
                cur.execute(rev)
                to = cur.fetchall()
                to = pd.DataFrame.from_dict(to)
                if len(to) != 0:
                    rev1 = to.iat[0, 0]
                    val = rev1 / aov * 100
                    data_dict = {'player_id': pl, 'start_date': sd, 'end_date': ed, 'parameter_id': par_out, 'value': val,
                                 'date_created': date.today(), 'source': 'Benchmarks', 'parametertree_id': 52, 'report_version_id': rep_ver_id}
                    required_rows.append(tuple(data_dict.values()))
            cur.close()
            self.InsertORUpdate(required_rows, db)
            print("Foodtech:- calc2 finished")
        except Exception as e:
            print("Foodtech:- Error in calc2:- ", e)

    def calc3(self, db):
        try:
            cur = db.cursor()
            s = (
                'update content_data.main_data set `val_copy`=-`value` where parameter_id in (850,851,852,855,420,421,1730,422,3541,3542,3543);'
            )
            cur.execute(s)
            db.commit()
            s = (
                'update content_data.main_data set `val_copy`=`value` where parameter_id in (848,849,854,417,418,419,1729,1727,3539,3540);'
            )
            cur.execute(s)
            db.commit()
            cur.close()
            print("Foodtech:- calc3 finished")
        except Exception as e:
            print("Foodtech:- Error in calc3:- ", e)

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
            self.InsertORUpdate(required_rows, db)
            print("Foodtech:- WA_Calc finished")
        except Exception as e:
            print("Foodtech:- Error in WA_Calc:- ", e)

    def calc_script(self, pl_id, sd, ed, db, id_name_dict, rep_ver_id):
        try:
            calc_dict = self.reset_calc_dict(id_name_dict)
            try:
                d = self.par_val_dict(pl_id, sd, ed, db, id_name_dict)
            except:
                pass
            try:
                calc_dict["340:Rest of India('000)"] = d["336:Pan India('000)"] - (
                    d["337:Top 10 cities('000)"] + d[
                        "338:Top 11-25 cities('000)"] + d["339:Top 26-50 cities('000)"]
                )
            except:
                pass
            try:
                calc_dict['3197:Pan India'] = d["336:Pan India('000)"
                                                ] * self.month_range(sd)
                calc_dict['3179:a) Top 10 cities'] = d["337:Top 10 cities('000)"
                                                       ] * self.month_range(sd)
                calc_dict['3180:b) Top 11-25 cities'] = d[
                    "338:Top 11-25 cities('000)"] * self.month_range(sd)
                calc_dict['3181:c) Top 26-50 cities'] = d[
                    "339:Top 26-50 cities('000)"] * self.month_range(sd)
                calc_dict['3182:d) Rest of India (exclusive top 50 cities)'
                          ] = calc_dict["340:Rest of India('000)"] * self.month_range(sd)
            except:
                pass
            try:
                calc_dict["1602:Rest of India(Exclusive M,T1,T2)('000)"] = d[
                    "336:Pan India('000)"] - (d["1599:Metro Cities('000)"] + d[
                        "1600:Tier-1 Cities('000)"] + d["1601:Tier-2 Cities('000)"])
                calc_dict['3183:Metro Cities'] = d["1599:Metro Cities('000)"
                                                   ] * self.month_range(sd)
                calc_dict['3184:Tier-1 Cities'] = d["1600:Tier-1 Cities('000)"
                                                    ] * self.month_range(sd)
                calc_dict['3185:Tier-2 Cities'] = d["1601:Tier-2 Cities('000)"
                                                    ] * self.month_range(sd)
                calc_dict['3186:Rest of India(Exclusive M,T1,T2)'] = calc_dict[
                    "1602:Rest of India(Exclusive M,T1,T2)('000)"] * self.month_range(sd
                                                                                      )
            except:
                pass
            try:
                calc_dict["352:Top 10 cities('000)"] = d["337:Top 10 cities('000)"
                                                         ] * (100 - d['342:Top 10 cities(%)']) / 100
            except:
                pass
            try:
                calc_dict["353:Top 11-25 cities('000)"] = d[
                    "338:Top 11-25 cities('000)"] * (100 - d[
                        '343:Top 11-25 cities(%)']) / 100
            except:
                pass
            try:
                calc_dict["354:Top 26-50 cities('000)"] = d[
                    "339:Top 26-50 cities('000)"] * (100 - d[
                        '344:Top 26-50 cities(%)']) / 100
            except:
                pass
            try:
                calc_dict["355:Rest of India('000)"] = calc_dict[
                    "340:Rest of India('000)"] * (100 - d[
                        '345:Rest of India (exclusive top 50 cities)(%)']) / 100
            except:
                pass
            try:
                calc_dict["1611:Metro Cities('000)"] = d["1599:Metro Cities('000)"
                                                         ] * (100 - d['1603:Metro Cities(%)']) / 100
            except:
                pass
            try:
                calc_dict["1612:Tier-1 Cities('000)"] = d[
                    "1600:Tier-1 Cities('000)"] * (100 - d['1604:Tier-1 Cities(%)']
                                                   ) / 100
            except:
                pass
            try:
                calc_dict["1613:Tier-2 Cities('000)"] = d[
                    "1601:Tier-2 Cities('000)"] * (100 - d['1605:Tier-2 Cities(%)']
                                                   ) / 100
            except:
                pass
            try:
                calc_dict["1614:Rest of India(Exclusive M,T1,T2)('000)"] = d[
                    "1602:Rest of India(Exclusive M,T1,T2)('000)"] * (100 - d[
                        '1606:Rest of India(Exclusive M,T1,T2)(%)']) / 100
            except:
                pass
            try:
                calc_dict['361:Pan India(INR)'] = (d['362:Top 10 cities(INR)'] *
                                                   d["337:Top 10 cities('000)"] + d[
                    "338:Top 11-25 cities('000)"] * d[
                    '363:Top 11-25 cities(INR)'] + d[
                    '364:Top 26-50 cities(INR)'] * d[
                    "339:Top 26-50 cities('000)"] + d[
                    '365:Rest of India (exclusive top 50 cities) (INR)'] *
                    calc_dict["340:Rest of India('000)"]) / (d[
                        "337:Top 10 cities('000)"] + d["338:Top 11-25 cities('000)"
                                                       ] + d["339:Top 26-50 cities('000)"] + calc_dict[
                        "340:Rest of India('000)"])
            except:
                pass
            try:
                calc_dict['366:Pan India(INR)'] = (d['367:Top 10 cities(INR)'] *
                                                   d["337:Top 10 cities('000)"] + d[
                    "338:Top 11-25 cities('000)"] * d[
                    '368:Top 11-25 cities(INR)'] + d[
                    '369:Top 26-50 cities(INR)'] * d[
                    "339:Top 26-50 cities('000)"] + d[
                    '370:Rest of India (exclusive top 50 cities) (INR)'] *
                    calc_dict["340:Rest of India('000)"]) / (d[
                        "337:Top 10 cities('000)"] + d["338:Top 11-25 cities('000)"
                                                       ] + d["339:Top 26-50 cities('000)"] + calc_dict[
                        "340:Rest of India('000)"])
            except:
                pass
            try:
                calc_dict['356:Pan India(INR)'] = calc_dict['366:Pan India(INR)'
                                                            ] - calc_dict['361:Pan India(INR)']
            except:
                pass
            try:
                calc_dict['357:Top 10 cities(INR)'] = d['367:Top 10 cities(INR)'
                                                        ] - d['362:Top 10 cities(INR)']
            except:
                pass
            try:
                calc_dict['358:Top 11-25 cities(INR)'] = d[
                    '368:Top 11-25 cities(INR)'] - d['363:Top 11-25 cities(INR)']
            except:
                pass
            try:
                calc_dict['359:Top 26-50 cities(INR)'] = d[
                    '369:Top 26-50 cities(INR)'] - d['364:Top 26-50 cities(INR)']
            except:
                pass
            try:
                calc_dict['360:Rest of India(INR)'] = d[
                    '370:Rest of India (exclusive top 50 cities) (INR)'] - d[
                    '365:Rest of India (exclusive top 50 cities) (INR)']
            except:
                pass
            try:
                calc_dict['1615:Metro Cities(INR)'] = d['1623:Metro Cities(INR)'
                                                        ] - d['1619:Metro Cities(INR)']
            except:
                pass
            try:
                calc_dict['1616:Tier-1 Cities(INR)'] = d['1624:Tier-1 Cities(INR)'
                                                         ] - d['1620:Tier-1 Cities(INR)']
            except:
                pass
            try:
                calc_dict['1617:Tier-2 Cities(INR)'] = d['1625:Tier-2 Cities(INR)'
                                                         ] - d['1621:Tier-2 Cities(INR)']
            except:
                pass
            try:
                calc_dict['1618:Rest of India(Exclusive M,T1,T2)(INR)'] = d[
                    '1626:Rest of India(Exclusive M,T1,T2)(INR)'] - d[
                    '1622:Rest of India(Exclusive M,T1,T2)(INR)']
            except:
                pass
            try:
                calc_dict['371:Pan India(INR Cr)'] = self.month_range(sd) * d[
                    "336:Pan India('000)"] * calc_dict['366:Pan India(INR)'
                                                       ] / 10 ** 4
            except:
                pass
            try:
                calc_dict['372:Top 10 cities(INR Cr)'] = self.month_range(sd) * d[
                    "337:Top 10 cities('000)"] * d['367:Top 10 cities(INR)'
                                                   ] / 10 ** 4
            except:
                pass
            try:
                calc_dict['373:Top 11-25 cities(INR Cr)'] = self.month_range(sd) * d[
                    "338:Top 11-25 cities('000)"] * d['368:Top 11-25 cities(INR)'
                                                      ] / 10 ** 4
            except:
                pass
            try:
                calc_dict['374:Top 26-50 cities(INR Cr)'] = self.month_range(sd) * d[
                    "339:Top 26-50 cities('000)"] * d['369:Top 26-50 cities(INR)'
                                                      ] / 10 ** 4
            except:
                pass
            try:
                calc_dict['375:Rest of India(INR Cr)'] = calc_dict[
                    '371:Pan India(INR Cr)'] - (calc_dict[
                        '372:Top 10 cities(INR Cr)'] + calc_dict[
                        '373:Top 11-25 cities(INR Cr)'] + calc_dict[
                        '374:Top 26-50 cities(INR Cr)'])
            except:
                pass
            try:
                calc_dict['1627:Metro Cities(INR Cr)'] = self.month_range(sd) * d[
                    "1599:Metro Cities('000)"] * d['1623:Metro Cities(INR)'
                                                   ] / 10 ** 4
            except:
                pass
            try:
                calc_dict['1628:Tier-1 Cities(INR Cr)'] = self.month_range(sd) * d[
                    "1600:Tier-1 Cities('000)"] * d['1624:Tier-1 Cities(INR)'
                                                    ] / 10 ** 4
            except:
                pass
            try:
                calc_dict['1629:Tier-2 Cities(INR Cr)'] = self.month_range(sd) * d[
                    "1601:Tier-2 Cities('000)"] * d['1625:Tier-2 Cities(INR)'
                                                    ] / 10 ** 4
            except:
                pass
            try:
                calc_dict['1630:Rest of India(Exclusive M,T1,T2)(INR Cr)'
                          ] = calc_dict['371:Pan India(INR Cr)'] - (calc_dict[
                              '1627:Metro Cities(INR Cr)'] + calc_dict[
                              '1628:Tier-1 Cities(INR Cr)'] + calc_dict[
                              '1629:Tier-2 Cities(INR Cr)'])
            except:
                pass
            try:
                calc_dict['323:Top 10 cities(%)'] = calc_dict[
                    '372:Top 10 cities(INR Cr)'] / calc_dict[
                    '371:Pan India(INR Cr)'] * 100
            except:
                pass
            try:
                calc_dict['324:Top 11-25 cities(%)'] = calc_dict[
                    '373:Top 11-25 cities(INR Cr)'] / calc_dict[
                    '371:Pan India(INR Cr)'] * 100
            except:
                pass
            try:
                calc_dict['325:Top 26-50 cities(%)'] = calc_dict[
                    '374:Top 26-50 cities(INR Cr)'] / calc_dict[
                    '371:Pan India(INR Cr)'] * 100
            except:
                pass
            try:
                calc_dict['326:Remaining Cities(%)'] = calc_dict[
                    '375:Rest of India(INR Cr)'] / calc_dict[
                    '371:Pan India(INR Cr)'] * 100
            except:
                pass
            try:
                calc_dict['1632:Metro Cities(%)'] = calc_dict[
                    '1627:Metro Cities(INR Cr)'] / calc_dict[
                    '371:Pan India(INR Cr)'] * 100
            except:
                pass
            try:
                calc_dict['1633:Tier-1 Cities(%)'] = calc_dict[
                    '1628:Tier-1 Cities(INR Cr)'] / calc_dict[
                    '371:Pan India(INR Cr)'] * 100
            except:
                pass
            try:
                calc_dict['1634:Tier-2 Cities(%)'] = calc_dict[
                    '1629:Tier-2 Cities(INR Cr)'] / calc_dict[
                    '371:Pan India(INR Cr)'] * 100
            except:
                pass
            try:
                calc_dict['1635:Rest of India(Exclusive M,T1,T2)(%)'] = calc_dict[
                    '1630:Rest of India(Exclusive M,T1,T2)(INR Cr)'] / calc_dict[
                    '371:Pan India(INR Cr)'] * 100
            except:
                pass
            try:
                calc_dict["1642:Delhi NCR ('000s)"] = d["1643:Delhi ('000s)"] + d[
                    "1644:Noida ('000s)"] + d["1645:Gurgaon ('000s)"]
            except:
                pass
            try:
                calc_dict['1686:Bengaluru(INR Cr)'] = d['1663:Bengaluru(INR)'] * d[
                    "1640:Bengaluru ('000s)"] * self.month_range(sd) / 10 ** 4
                calc_dict['1687:Hyderabad(INR Cr)'] = d['1664:Hyderabad(INR)'] * d[
                    "1641:Hyderabad ('000s)"] * self.month_range(sd) / 10 ** 4
                calc_dict['1689:Delhi (INR Cr)'] = d['1666:Delhi (INR)'] * d[
                    "1643:Delhi ('000s)"] * self.month_range(sd) / 10 ** 4
                calc_dict['1690:Noida(INR Cr)'] = d['1667:Noida(INR)'] * d[
                    "1644:Noida ('000s)"] * self.month_range(sd) / 10 ** 4
                calc_dict['1691:Gurgaon(INR Cr)'] = d['1668:Gurgaon(INR)'] * d[
                    "1645:Gurgaon ('000s)"] * self.month_range(sd) / 10 ** 4
                calc_dict['1688:Delhi NCR(INR Cr)'] = calc_dict[
                    '1689:Delhi (INR Cr)'] + calc_dict['1690:Noida(INR Cr)'
                                                       ] + calc_dict['1691:Gurgaon(INR Cr)']
                calc_dict['1692:Mumbai(INR Cr)'] = d['1669:Mumbai(INR)'] * d[
                    "1646:Mumbai ('000s)"] * self.month_range(sd) / 10 ** 4
                calc_dict['1693:Chennai(INR Cr)'] = d['1670:Chennai(INR)'] * d[
                    "1647:Chennai ('000s)"] * self.month_range(sd) / 10 ** 4
                calc_dict['1694:Kolkata(INR Cr)'] = d['1671:Kolkata(INR)'] * d[
                    "1648:Kolkata ('000s)"] * self.month_range(sd) / 10 ** 4
                calc_dict['1695:Pune(INR Cr)'] = d['1672:Pune(INR)'] * d[
                    "1649:Pune ('000s)"] * self.month_range(sd) / 10 ** 4
                calc_dict['1696:Ahmedabad(INR Cr)'] = d['1673:Ahmedabad(INR)'] * d[
                    "1650:Ahmedabad ('000s)"] * self.month_range(sd) / 10 ** 4
                calc_dict['1697:Jaipur(INR Cr)'] = d['1674:Jaipur(INR)'] * d[
                    "1651:Jaipur('000s)"] * self.month_range(sd) / 10 ** 4
                calc_dict['1698:Coimbatore(INR Cr)'] = d['1675:Coimbatore(INR)'
                                                         ] * d["1652:Coimbatore ('000s)"] * self.month_range(sd) / 10 ** 4
                calc_dict['1699:Lucknow(INR Cr)'] = d['1676:Lucknow(INR)'] * d[
                    "1653:Lucknow ('000s)"] * self.month_range(sd) / 10 ** 4
                calc_dict['1700:Chandigarh(INR Cr)'] = d['1677:Chandigarh(INR)'
                                                         ] * d["1654:Chandigarh ('000s)"] * self.month_range(sd) / 10 ** 4
                calc_dict['1701:Vizag(INR Cr)'] = d['1678:Vizag(INR)'] * d[
                    "1655:Vizag ('000s)"] * self.month_range(sd) / 10 ** 4
                calc_dict['1702:Kochi(INR Cr)'] = d['1679:Kochi(INR)'] * d[
                    "1656:Kochi ('000s)"] * self.month_range(sd) / 10 ** 4
                calc_dict['1703:Indore(INR Cr)'] = d['1680:Indore(INR)'] * d[
                    "1657:Indore ('000s)"] * self.month_range(sd) / 10 ** 4
                calc_dict['1704:Surat(INR Cr)'] = d['1681:Surat(INR)'] * d[
                    "1658:Surat ('000s)"] * self.month_range(sd) / 10 ** 4
                calc_dict['1705:Nagpur(INR Cr)'] = d['1682:Nagpur(INR)'] * d[
                    "1659:Nagpur ('000s)"] * self.month_range(sd) / 10 ** 4
                calc_dict['1706:Patna(INR Cr)'] = d['1683:Patna(INR)'] * d[
                    "1660:Patna ('000s)"] * self.month_range(sd) / 10 ** 4
                calc_dict['1707:Kanpur(INR Cr)'] = d['1684:Kanpur(INR)'] * d[
                    "1661:Kanpur ('000s)"] * self.month_range(sd) / 10 ** 4
                calc_dict['1708:Kozhikode(INR Cr)'] = d['1685:Kozhikode(INR)'] * d[
                    "1662:Kozhikode ('000s)"] * self.month_range(sd) / 10 ** 4
            except:
                pass
            try:
                calc_dict['1665:Delhi NCR(INR)'] = calc_dict[
                    '1688:Delhi NCR(INR Cr)'] / (calc_dict[
                        "1642:Delhi NCR ('000s)"] * self.month_range(sd)) * 10000
            except:
                pass
            try:
                calc_dict['2862:% Non Super/Pro orders'] = 100 - d[
                    '2861:% Super/Pro orders']
            except:
                pass
            try:
                calc_dict['313:borne by platform(%)'] = 100 - d[
                    '312:borne by restaurant(%)']
            except:
                pass
            try:
                calc_dict['316:% of non-discounted orders(%)'] = 100 - d[
                    '315:% of discounted orders (%)']
            except:
                pass
            try:
                calc_dict['319:Other prepaid modes(%)'] = 100 - d[
                    '317:COD (Cash on Delivery)(%)']
            except:
                pass
            try:
                calc_dict['322:Restaurant(%)'] = 100 - (d['320:Own(%)'] + d[
                    '321:Partner (3PL)(%)'])
            except:
                pass
            try:
                calc_dict['1710:% of orders on Weekend(%)'] = 100 - d[
                    '1709:% of orders on Weekday(%)']
            except:
                pass
            try:
                calc_dict['1715:% of Late Night(%)'] = 100 - (d[
                    '1712:% of Lunch(%)'] + d['1713:% of Snacks(%)'] + d[
                    '1714:% of Dinner(%)'] + d['1711:% of Breakfast(%)'])
            except:
                pass
            try:
                calc_dict['1716:Website/M.site(%)'] = 100 - d['1717:App(%)']
            except:
                pass
            try:
                calc_dict['1720:AOV excluding delivery fees(INR)'] = d[
                    '1718:AOV  (Inc.Del fees- Pre Discount)(INR)'] - d[
                    '1719:Delivery fees(INR)']
            except:
                pass
            try:
                calc_dict['1724:AOV post discounts(INR)'] = calc_dict[
                    '1720:AOV excluding delivery fees(INR)'] - d[
                    '1723:Overall discounts offered to customer(INR)']
            except:
                pass
            try:
                calc_dict['3168:AOV (Exc.Del fees- Post Discount)(INR)'
                          ] = calc_dict['1720:AOV excluding delivery fees(INR)'] - d[
                    '1723:Overall discounts offered to customer(INR)']
            except:
                pass
            try:
                calc_dict['1730:Cost per Order(INR)'] = d[
                    '421:Delivery Cost per order(INR)'] + d[
                    '422:Other costs� per order(INR)'] + d[
                    '420:Discounting Cost per order(INR)']
            except:
                pass
            try:
                calc_dict["351:Pan India('000)"] = calc_dict[
                    "352:Top 10 cities('000)"] + calc_dict[
                    "353:Top 11-25 cities('000)"] + calc_dict[
                    "354:Top 26-50 cities('000)"] + calc_dict[
                    "355:Rest of India('000)"]
            except:
                pass
            try:
                calc_dict['341:Pan India(%)'] = (d["336:Pan India('000)"] -
                                                 calc_dict["351:Pan India('000)"]) / d["336:Pan India('000)"
                                                                                       ] * 100
            except:
                pass
            try:
                calc_dict["306:Cancelled orders ('000)"] = d["336:Pan India('000)"
                                                             ] * calc_dict['341:Pan India(%)'] / 100
            except:
                pass
            try:
                calc_dict["307:Fulfilled orders ('000)"] = d["336:Pan India('000)"
                                                             ] * (100 - calc_dict['341:Pan India(%)']) / 100
            except:
                pass
            try:
                calc_dict['333:Number of orders per rider per month(#)'] = d[
                    "336:Pan India('000)"] * self.month_range(sd) / d[
                    "332:Total number of active DE's of the month('000)"]
            except:
                pass
            try:
                calc_dict[
                    '334:Number of orders per rider per day (Assuming 24 days of working for each DE)(#)'
                ] = calc_dict['333:Number of orders per rider per month(#)'
                              ] / 24
            except:
                pass
            try:
                calc_dict["335:Average monthly payout to DE's(INR)"] = calc_dict[
                    '333:Number of orders per rider per month(#)'] * d[
                    '329:Cost per delivery (delivery executive payouts, incentives, surge)(INR)'
                ]
            except:
                pass
            try:
                calc_dict['1727:Revenue per Order(INR)'] = d[
                    '1729:Delivery Fees charged to customer(%)'] + d[
                    '417:Commissions revenue per order(INR)']
            except:
                pass
            try:
                calc_dict['1731:Contribution Margin(INR)'] = calc_dict[
                    '1727:Revenue per Order(INR)'] - calc_dict[
                    '1730:Cost per Order(INR)']
            except:
                pass
            try:
                calc_dict['806:% Contribution margin'] = calc_dict[
                    '1731:Contribution Margin(INR)'] / calc_dict[
                    '1720:AOV excluding delivery fees(INR)']
            except:
                pass
            try:
                calc_dict['1332:Transaction Frequency'] = d["336:Pan India('000)"
                                                            ] * self.month_range(sd) / d['238:Monthly Transacting Users (Mn)'
                                                                                         ] / 10 ** 3
            except:
                pass
            required_rows = []
            for k in calc_dict:
                if not calc_dict[k]:
                    continue
                parameter_id, parameter_name = k.split(':')
                parameter_id = int(parameter_id)
                data_dict = {'player_id': pl_id, 'start_date': str(sd),
                             'end_date': str(ed), 'parameter_id': parameter_id, 'value':
                             calc_dict[k], 'date_created': str(date.today()), 'source':
                             'webforms_calc', 'parametertree_id': 52, 'report_version_id': rep_ver_id}
                required_rows.append(tuple(data_dict.values()))
            self.InsertORUpdate(required_rows, db)
            print("Foodtech:- calc_script finished")
        except Exception as e:
            print("Foodtech:- Error in calc_script:- ", e)

    def report_version_id(self, rep_ver_id):
        print("Foodtech:- calculate prapameter script started for report_version_id=", rep_ver_id)
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
            WA_input_df = self.get_WA_sheet('Food')
            self.WA_Calc(player_id, WA_input_df, sd, ed, db, rep_ver_id)
            self.calc1(player_id, sd, ed, db, rep_ver_id)
            self.calc2(player_id, sd, ed, db, rep_ver_id)
            self.calc3(db)
            print("Foodtech:- report_version_id finished")
        except Exception as e:
            print("Foodtech:- Error in report_version_id:- ", e)
