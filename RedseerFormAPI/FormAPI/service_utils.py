import pandas as pd
import os
import pymysql
import calendar
import pymysql

import datetime
from datetime import datetime
from datetime import date
import calendar
from calendar import monthrange
import sys

# change address in cursor
class CalculatedParamFn:
    @staticmethod
    def par_val_dict(pl_id, sd, ed):
        db = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='redroot',
            password="seer#123",
            db='content_data',
            ssl={'ssl': {'tls': True}}
        )

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
        for i in range(1, 4000):
            try:
                ans[i]
            except:
                ans[i] = 0
        return ans

    @staticmethod
    def month_range(sd):
        yr = int(sd[:4])
        month = int(sd[5:7])
        Total_number_days = calendar.monthrange(yr, month)[1]
        return Total_number_days

    @staticmethod
    def InsertORUpdate(dff):
        data_dict = dff.to_dict(orient='records')
        db = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='redroot',
            password="seer#123",
            db='content_data',
            ssl={'ssl': {'tls': True}}
        )

        for i in data_dict:
            comp_id = i['player_id']
            s_d = i['start_date']
            e_d = i['end_date']
            par_id = i['parameter_id']
            val = i['value']
            dc = i['date_created']
            s = i['source']
            ptree = i['parametertree_id']
            a = "SELECT * from main_data WHERE player_id= '" + str(comp_id) + "' AND start_date= '" + str(
                s_d) + "'" + " AND end_date='" + str(e_d) + "'" + \
                " AND parameter_id=" + '"' + str(par_id) + '";'
            cur = db.cursor()
            row_exist = cur.execute(a)
            if row_exist == 0:
                b = "insert into main_data(player_id,start_date,end_date,parameter_id,value,date_created,source,parametertree_id) values('" + str(
                    comp_id) + "','" + str(s_d) + "', '" + str(e_d) + "','" + str(par_id) + "','" + str(
                    val) + "', '" + str(dc) + "','" + s + "','" + str(ptree) + "')"
                print(b)
                cur.execute(b)
                db.commit()
            else:
                b = "Update main_data set value='" + str(val) + "' where player_id= '" + str(
                    comp_id) + "' AND start_date= '" + str(s_d) + "'" + " AND end_date='" + str(
                    e_d) + "'" + " AND parameter_id=" + '"' + str(par_id) + '";'
                print(b)
                cur.execute(b)
                db.commit()
            cur.close()

    @staticmethod
    def ind_players(a):
        db = pymysql.connect(
            host='127.0.0.1',
            port=3306,
            user='redroot',
            password="seer#123",
            db='content_data',
            ssl={'ssl': {'tls': True}}
        )
        cur = db.cursor()
        cur.execute("select * from player where industry_id= '" + str(a) + "';")
        pl = cur.fetchall()
        cur.close()
        pl = pd.DataFrame.from_dict(pl)
        pl = pl[[0]]
        pl = list(pl[0])
        return pl

    @staticmethod
    def reset_calc_dict():
        calc_dict = {}
        for i in range(1, 4000):
            calc_dict[i] = 0;

    def calc_script_eb2b(self, pl_id, sd, ed):
        # print(pl_id)
        # self.reset_calc_dict()
        calc_dict = {}
        for i in range(1, 4000):
            calc_dict[i] = 0
        try:
            d = self.par_val_dict(pl_id, sd, ed)
        except:
            pass
        try:
            calc_dict[2593] = (d[2592] / d[2588]) / self.month_range(sd)
        except:
            pass
        try:
            calc_dict[2596] = (d[2592] / d[2590]) / self.month_range(sd)
        except:
            pass
        try:
            calc_dict[2600] = 100 - d[2599]
            calc_dict[2602] = 100 - d[2601]
            calc_dict[2606] = 100 - d[2605]
        except:
            pass
        #     try:
        #         calc_dict[2610]=d[2598]/d[]
        #     except:
        #         pass
        try:
            calc_dict[2612] = (d[2611](100 - d[2617])) / 100
            calc_dict[2613] = (d[2612](100 - d[2618] - d[2619])) / 100
            calc_dict[2622] = d[2611] - d[2620] - d[2621]
        except:
            pass
        try:
            calc_dict[2623] = (d[2620] / d[2626]) * 10000
        except:
            pass
        try:
            calc_dict[2624] = (d[2621] / d[2627]) * 10000
        except:
            pass
        try:
            calc_dict[2625] = (calc_dict[2622] / d[2628]) * 10000
        except:
            pass

        calc_dict[3172] = calc_dict[2623] + calc_dict[2624] + calc_dict[2625]

        try:
            calc_dict[3173] = (d[2611] / calc_dict[3172]) * 10000
        except:
            pass
        try:
            calc_dict[2630] = 100 - d[2629]
            calc_dict[2633] = 100 - d[2631] - d[2632]
        except:
            pass

        required_df = []
        for k in calc_dict:
            if calc_dict[k] == 0:
                continue
            print(k, calc_dict[k])
            required_df.append({"player_id": pl_id, 'start_date': str(sd), 'end_date': str(ed), 'parameter_id': k,
                                'value': calc_dict[k], "date_created": date.today(), "source": 'webforms_calc',
                                'parametertree_id': 52})
        dff = pd.DataFrame(required_df)
        self.InsertORUpdate(dff)

    def calc_script_eb2bGrocery(self, pl_id, sd, ed):
        calc_dict = {}
        for i in range(1, 4000):
            calc_dict[i] = 0
        try:
            d = self.par_val_dict(pl_id, sd, ed)
        except:
            pass
        try:
            calc_dict[2593] = (d[2592] / d[2588]) / self.month_range(sd)
        except:
            pass
        try:
            calc_dict[2596] = (d[2592] / d[2590]) / self.month_range(sd)
        except:
            pass
        try:
            calc_dict[2600] = 100 - d[2599]
            calc_dict[2602] = 100 - d[2601]
            calc_dict[2606] = 100 - d[2605]
        except:
            pass
            #     try:
            #         calc_dict[2610]=d[2598]/d[]
            #     except:
            #         pass
        try:
            calc_dict[2612] = (d[2611](100 - d[2617])) / 100
            calc_dict[2613] = (d[2612](100 - d[2618] - d[2619])) / 100
            calc_dict[2657] = d[2611] - d[2653] - d[2654] - d[2655] - d[2656]
        except:
            pass
        try:
            calc_dict[2658] = (d[2653] / d[2663]) * 10000
        except:
            pass
        try:
            calc_dict[2659] = (d[2654] / d[2664]) * 10000
        except:
            pass
        try:
            calc_dict[2660] = (d[2655] / d[2665]) * 10000
        except:
            pass
        try:
            calc_dict[2661] = (d[2656] / d[2666]) * 10000
        except:
            pass
        try:
            calc_dict[2662] = (calc_dict[2657] / d[2667]) * 10000
        except:
            pass

        calc_dict[3172] = calc_dict[2658] + calc_dict[2659] + calc_dict[2660] + calc_dict[2661] + calc_dict[2662]

        try:
            calc_dict[3173] = (d[2611] / calc_dict[3172]) * 10000
        except:
            pass

        try:
            calc_dict[2630] = 100 - d[2629]
            calc_dict[2633] = 100 - d[2631] - d[2632]
        except:
            pass

        required_df = []
        for k in calc_dict:
            if calc_dict[k] == 0:
                continue
            print(k, calc_dict[k])
            required_df.append({"player_id": pl_id, 'start_date': str(sd), 'end_date': str(ed), 'parameter_id': k,
                                'value': calc_dict[k], "date_created": date.today(), "source": 'webforms_calc',
                                'parametertree_id': 52})
        dff = pd.DataFrame(required_df)
        print(dff)
        self.InsertORUpdate(dff)

    def calc_script_eb2bElectronics(self ,pl_id, sd, ed):
            calc_dict = {}
            for i in range(1, 4000):
                calc_dict[i] = 0
            try:
                d = self.par_val_dict(pl_id, sd, ed)
            except:
                pass
            try:
                calc_dict[2593] = (d[2592] / d[2588]) / self.month_range(sd)
            except:
                pass
            try:
                calc_dict[2596] = (d[2592] / d[2590]) / self.month_range(sd)
            except:
                pass
            try:
                calc_dict[2600] = 100 - d[2599]
                calc_dict[2602] = 100 - d[2601]
                calc_dict[2606] = 100 - d[2605]
            except:
                pass
            #     try:
            #         calc_dict[2610]=d[2598]/d[]
            #     except:
            #         pass
            try:
                calc_dict[2612] = (d[2611](100 - d[2617])) / 100
                calc_dict[2613] = (d[2612](100 - d[2618] - d[2619])) / 100
            except:
                pass
            calc_dict[3172] = d[2679] + d[2680] + d[2681] + d[2682] + d[2683]

            try:
                calc_dict[2658] = (d[2653] / d[2663]) * 10000
            except:
                pass
            try:
                calc_dict[2684] = (d[2668] / d[2679]) * 10000
            except:
                pass
            try:
                calc_dict[2685] = (d[2675] / d[2680]) * 10000
            except:
                pass
            try:
                calc_dict[2686] = (d[2676] / d[2681]) * 10000
            except:
                pass
            try:
                calc_dict[2687] = (d[2677] / d[2682]) * 10000
            except:
                pass
            try:
                calc_dict[2688] = (d[2678] / d[2683]) * 10000
            except:
                pass
            try:
                calc_dict[3173] = (d[2611] / calc_dict[3172]) * 10000
            except:
                pass

            try:
                calc_dict[2630] = 100 - d[2629]
                calc_dict[2633] = 100 - d[2631] - d[2632]
            except:
                pass

            required_df = []
            for k in calc_dict:
                if calc_dict[k] == 0:
                    continue
                print(k, calc_dict[k])
                required_df.append({"player_id": pl_id, 'start_date': str(sd), 'end_date': str(ed), 'parameter_id': k,
                                    'value': calc_dict[k], "date_created": date.today(), "source": 'webforms_calc',
                                    'parametertree_id': 52})
            dff = pd.DataFrame(required_df)
            print(dff)
            self.InsertORUpdate(dff)

    def calc_script_eb2bEPharma(self, pl_id,sd,ed):
        calc_dict = {}
        for i in range(1, 4000):
            calc_dict[i] = 0
        try:
            d = self.par_val_dict(pl_id, sd, ed)
        except:
            pass
        try:
            calc_dict[2593] = (d[2592] / d[2588]) / self.month_range(sd)
        except:
            pass
        try:
            calc_dict[2596] = (d[2592] / d[2590]) / self.month_range(sd)
        except:
            pass
        try:
            calc_dict[2600] = 100 - d[2599]
            calc_dict[2602] = 100 - d[2601]
            calc_dict[2606] = 100 - d[2605]
        except:
            pass
            #     try:
            #         calc_dict[2610]=d[2598]/d[]
            #     except:
            #         pass
        try:
            calc_dict[2612] = (d[2611](100 - d[2617])) / 100
            calc_dict[2613] = (d[2612](100 - d[2618] - d[2619])) / 100
            calc_dict[3261] = d[2611] - d[2669] - d[2670]
        except:
            pass

        try:
            calc_dict[2671] = (d[2669] / d[2673]) * 10000
        except:
            pass
        try:
            calc_dict[2672] = (d[2670] / d[2674]) * 10000
        except:
            pass
        try:
            calc_dict[3245] = (calc_dict[3261] / d[3262]) * 10000
        except:
            pass

        calc_dict[3172] = calc_dict[2671] + calc_dict[2672] + calc_dict[3245]

        try:
            calc_dict[3173] = (d[2611] / calc_dict[3172]) * 10000
        except:
            pass

        try:
            calc_dict[2630] = 100 - d[2629]
            calc_dict[2633] = 100 - d[2631] - d[2632]
        except:
            pass

        required_df = []
        for k in calc_dict:
            if calc_dict[k] == 0:
                continue
            print(k, calc_dict[k])
            required_df.append({"player_id": pl_id, 'start_date': str(sd), 'end_date': str(ed), 'parameter_id': k,
                                'value': calc_dict[k], "date_created": date.today(), "source": 'webforms_calc',
                                'parametertree_id': 52})
        dff = pd.DataFrame(required_df)
        print(dff)
        self.InsertORUpdate(dff)

    def calc_script_csm(self, pl_id, sd,ed):
        calc_dict = {}
        for i in range(1, 4000):
            calc_dict[i] = 0
        try:
            d = self.par_val_dict(pl_id, sd, ed)
        except:
            pass
        try:
            calc_dict[35] = (d[34] / d[52]) * 100
        except:
            pass
        calc_dict[24] = d[8] * d[2]
        calc_dict[128] = calc_dict[24] * d[34] * self.month_range(sd)
        calc_dict[110] = 100 - d[101] - d[103]
        calc_dict[67] = 100 - d[61] - d[63]
        calc_dict[169] = 100 - d[53] - d[54] - d[55] - d[56]
        calc_dict[176] = 100 - d[175] - d[177] - d[178]
        calc_dict[181] = 100 - d[179] - d[180]
        calc_dict[184] = 100 - d[182] - d[183]
        calc_dict[189] = 100 - d[204] - d[205] - d[206] - d[207]
        calc_dict[196] = 100 - d[195] - d[197] - d[198]

        required_df = []
        for k in calc_dict:
            if calc_dict[k] == 0:
                continue
            print(k, calc_dict[k])
            required_df.append({"player_id": pl_id, 'start_date': str(sd), 'end_date': str(ed), 'parameter_id': k,
                                'value': calc_dict[k], "date_created": date.today(), "source": 'webforms_calc',
                                'parametertree_id': 52})
        dff = pd.DataFrame(required_df)
        print(dff)
        self.InsertORUpdate(dff)

    def calc_script_shortform(self, pl_id, sd, ed):
        calc_dict = {}
        for i in range(1, 4000):
            calc_dict[i] = 0
        try:
            d = self.par_val_dict(pl_id, sd, ed)
        except:
            pass
        try:
            calc_dict[35] = (d[34] / d[52]) * 100
        except:
            pass
        calc_dict[24] = d[8] * d[2]
        calc_dict[128] = calc_dict[24] * d[34] * self.month_range(sd)
        calc_dict[110] = 100 - d[101] - d[103]
        calc_dict[67] = 100 - d[61] - d[63]
        calc_dict[169] = 100 - d[166] - d[167] - d[168]
        calc_dict[176] = 100 - d[175] - d[177] - d[178]
        calc_dict[181] = 100 - d[179] - d[180]
        calc_dict[184] = 100 - d[182] - d[183]
        calc_dict[189] = 100 - d[187] - d[186] - d[188]
        calc_dict[196] = 100 - d[195] - d[197] - d[198]

        required_df = []
        for k in calc_dict:
            if calc_dict[k] == 0:
                continue
            print(k, calc_dict[k])
            required_df.append({"player_id": pl_id, 'start_date': str(sd), 'end_date': str(ed), 'parameter_id': k,
                                'value': calc_dict[k], "date_created": date.today(), "source": 'webforms_calc',
                                'parametertree_id': 52})
        dff = pd.DataFrame(required_df)
        print(dff)
        self.InsertORUpdate(dff)

    def calc_script_video(self, pl_id, sd, ed):
        calc_dict = {}
        for i in range(1, 4000):
            calc_dict[i] = 0
        try:
            d = self.par_val_dict(pl_id, sd, ed)
        except:
            pass
        try:
            calc_dict[35] = (d[34] / d[52]) * 100
        except:
            pass
        calc_dict[24] = d[8] * d[2]
        calc_dict[128] = calc_dict[24] * d[34] * self.month_range(sd)
        calc_dict[110] = 100 - d[101] - d[103]
        calc_dict[67] = 100 - d[61] - d[63]
        calc_dict[169] = 100 - d[166] - d[167] - d[168]
        calc_dict[176] = 100 - d[175] - d[177] - d[178]
        calc_dict[181] = 100 - d[179] - d[180]
        calc_dict[184] = 100 - d[182] - d[183]
        calc_dict[189] = 100 - d[187] - d[186] - d[188]
        calc_dict[196] = 100 - d[195] - d[197] - d[198]
        calc_dict[203] = 100 - d[199] - d[200] - d[201] - d[202]

        required_df = []
        for k in calc_dict:
            if calc_dict[k] == 0:
                continue
            print(k, calc_dict[k])
            required_df.append({"player_id": pl_id, 'start_date': str(sd), 'end_date': str(ed), 'parameter_id': k,
                                'value': calc_dict[k], "date_created": date.today(), "source": 'webforms_calc',
                                'parametertree_id': 52})
        dff = pd.DataFrame(required_df)
        print(dff)
        self.InsertORUpdate(dff)

    def calc_script_audio(self, pl_id, sd, ed):
        calc_dict = {}
        for i in range(1, 4000):
            calc_dict[i] = 0
        try:
            d = self.par_val_dict(pl_id, sd, ed)
        except:
            pass
        try:
            calc_dict[35] = (d[34] / d[52]) * 100
        except:
            pass
        try:
            calc_dict[24] = d[8] * d[2]
            calc_dict[128] = calc_dict[24] * d[34] * self.month_range(sd)
        except:
            pass
        calc_dict[110] = 100 - d[101] - d[103]
        calc_dict[67] = 100 - d[61] - d[63]
        calc_dict[169] = 100 - d[166] - d[167] - d[168]
        calc_dict[176] = 100 - d[175] - d[177] - d[178]
        calc_dict[181] = 100 - d[179] - d[180]
        calc_dict[184] = 100 - d[182] - d[183]
        calc_dict[189] = 100 - d[187] - d[186] - d[188]
        calc_dict[196] = 100 - d[195] - d[197] - d[198]
        calc_dict[770] = 100 - d[766] - d[768]
        calc_dict[764] = d[754] + d[756] + d[758] + d[760]

        required_df = []
        for k in calc_dict:
            if calc_dict[k] == 0:
                continue
            print(k, calc_dict[k])
            required_df.append({"player_id": pl_id, 'start_date': str(sd), 'end_date': str(ed), 'parameter_id': k,
                                'value': calc_dict[k], "date_created": date.today(), "source": 'webforms_calc',
                                'parametertree_id': 52})
        dff = pd.DataFrame(required_df)
        print(dff)
        self.InsertORUpdate(dff)

    def calc_script_rmg(self, pl_id, sd, ed):
        calc_dict = {}
        for i in range(1, 4000):
            calc_dict[i] = 0
        try:
            d = self.par_val_dict(pl_id, sd, ed)
        except:
            pass

        try:
            calc_dict[1004] = (d[1002] / d[1000]) * 100
        except:
            pass
        try:
            calc_dict[1008] = d[1002] * d[1007] * self.month_range(sd)
        except:
            pass
        try:
            calc_dict[1022] = d[1000] * d[1020]
        except:
            pass
        try:
            calc_dict[1018] = (calc_dict[1022] / d[1021]) * 100
        except:
            pass
        try:
            calc_dict[1050] = d[1047] * d[1048]
        except:
            pass
        try:
            calc_dict[1046] = (calc_dict[1050] / d[1049]) * 100
        except:
            pass
        try:
            calc_dict[1042] = d[1039] * d[1040]
        except:
            pass
        try:
            calc_dict[1038] = (calc_dict[1042] / d[1041]) * 100
        except:
            pass
        try:
            calc_dict[1055] = d[1052] * d[1053]
        except:
            pass
        try:
            calc_dict[1051] = (calc_dict[1055] / d[1054]) * 100
        except:
            pass
        try:
            calc_dict[1060] = d[1057] * d[1058]
        except:
            pass
        try:
            calc_dict[1056] = (calc_dict[1060] / d[1059]) * 100
        except:
            pass
        try:
            calc_dict[1065] = d[1062] * d[1063]
        except:
            pass
        try:
            calc_dict[1061] = (calc_dict[1065] / d[1064]) * 100
        except:
            pass
        calc_dict[1026] = 100 - d[1023] - d[1024] - d[1025]
        calc_dict[1032] = d[1033] + d[1034]

        required_df = []
        for k in calc_dict:
            if calc_dict[k] == 0:
                continue
            print(k, calc_dict[k])
            required_df.append({"player_id": pl_id, 'start_date': str(sd), 'end_date': str(ed), 'parameter_id': k,
                                'value': calc_dict[k], "date_created": date.today(), "source": 'webforms_calc',
                                'parametertree_id': 52})
        dff = pd.DataFrame(required_df)
        print(dff)
        self.InsertORUpdate(dff)

    def calc_script_usedCars(self, pl_id, sd, ed):
        calc_dict = {}
        for i in range(1, 4000):
            calc_dict[i] = 0
        try:
            d = self.par_val_dict(pl_id, sd, ed)
        except:
            pass

        try:
            calc_dict[1586] = 100 - (d[1584] + d[1585])
            calc_dict[1202] = d[1193] - (d[1194] + d[1195] + d[1196] + d[1197] + d[1198] + d[1199] + d[1200] + d[1201])
            calc_dict[1213] = d[1214] - (d[1205] + d[1206] + d[1207] + d[1208] + d[1209] + d[1210] + d[1211] + d[1212])
            calc_dict[1217] = d[1192] + d[1193] - d[1214]
            calc_dict[1228] = d[1219] - (d[1220] + d[1221] + d[1222] + d[1223] + d[1224] + d[1225] + d[1226] + d[1227])
            calc_dict[1240] = d[1219] * d[1237]
            calc_dict[1242] = calc_dict[1240] - (100 - d[1241] * d[1219])
            calc_dict[1245] = calc_dict[1242] + d[1243]
            calc_dict[1247] = calc_dict[1245] - d[1246]
            calc_dict[1250] = calc_dict[1247] - d[1248] - d[1249]
        except:
            pass
        try:
            calc_dict[1587] = (calc_dict[1240] / d[1219]) * 100
        except:
            pass
        try:
            calc_dict[1588] = (calc_dict[1242] / d[1219]) * 100
        except:
            pass
        try:
            calc_dict[1589] = (d[1243] / d[1219]) * 100
        except:
            pass
        try:
            calc_dict[1591] = (d[1246] / d[1219]) * 100
        except:
            pass
        try:
            calc_dict[1592] = (calc_dict[1247] / d[1219]) * 100
        except:
            pass
        try:
            calc_dict[1593] = (d[1248] / d[1219]) * 100
        except:
            pass
        try:
            calc_dict[1595] = (calc_dict[1250] / d[1219]) * 100
        except:
            pass
        try:
            calc_dict[1167] = d[1214]
        except:
            pass

        try:
            calc_dict[1168] = (d[1165] / d[1163]) * 100
        except:
            pass
        try:
            calc_dict[1169] = (calc_dict[1167] / d[1165]) * 100
        except:
            pass
        try:
            calc_dict[1170] = (calc_dict[1167] / d[1163]) * 100
        except:
            pass

        try:
            calc_dict[1252] = d[1747] - (d[1184] + d[1185] + d[1186] + d[1187] + d[1188] + d[1189] + d[1190] + d[1191])
        except:
            pass

        required_df = []
        for k in calc_dict:
            if calc_dict[k] == 0:
                continue
            print(k, calc_dict[k])
            required_df.append({"player_id": pl_id, 'start_date': str(sd), 'end_date': str(ed), 'parameter_id': k,
                                'value': calc_dict[k], "date_created": date.today(), "source": 'webforms_calc',
                                'parametertree_id': 52})
        dff = pd.DataFrame(required_df)
        print(dff)
        self.InsertORUpdate(dff)

    def calc_script_meatCore(self, pl_id, sd, ed):
        calc_dict = {}
        for i in range(1, 4000):
            calc_dict[i] = 0
        try:
            d = self.par_val_dict(pl_id, sd, ed)
        except:
            pass

        calc_dict[1434] = d[1435] + d[1436] + d[1437]
        try:
            calc_dict[1438] = (d[1435] / d[240]) * 10000
        except:
            pass
        try:
            calc_dict[241] = d[1435]
        except:
            pass
        try:
            calc_dict[243] = d[1435](100 - d[242])
        except:
            pass
        try:
            calc_dict[244] = d[245] + d[246]
        except:
            pass
        try:
            calc_dict[247] = calc_dict[243](100 - d[244])
        except:
            pass
        try:
            calc_dict[381] = calc_dict[1438] / self.month_range(sd)
        except:
            pass
        calc_dict[1444] = 100 - (d[1439] + d[1440] + d[1441] + d[1442] + d[1443])
        calc_dict[1450] = 100 - (d[1445] + d[1446] + d[1447] + d[1448] + d[1449])
        calc_dict[1457] = 100 - (d[1452] + d[1453] + d[1454] + d[1455] + d[1456])
        calc_dict[1464] = 100 - (d[1459] + d[1460] + d[1461] + d[1462] + d[1463])
        calc_dict[1471] = 100 - (d[1466] + d[1467] + d[1468] + d[1469] + d[1470])
        calc_dict[1478] = 100 - (d[1473] + d[1474] + d[1475] + d[1476] + d[1477])
        calc_dict[1485] = 100 - (d[1480] + d[1481] + d[1482] + d[1483] + d[1484])

        calc_dict[1734] = (d[1733] * d[1732] * self.month_range(sd)) / 10000
        calc_dict[399] = (d[397] * d[398] * self.month_range(sd)) / 10000
        calc_dict[402] = (d[400] * d[401] * self.month_range(sd)) / 10000
        calc_dict[405] = (d[403] * d[404] * self.month_range(sd)) / 10000
        calc_dict[408] = (d[406] * d[407] * self.month_range(sd)) / 10000
        calc_dict[411] = (d[410] * d[409] * self.month_range(sd)) / 10000

        required_df = []
        for k in calc_dict:
            if calc_dict[k] == 0:
                continue
            print(k, calc_dict[k])
            required_df.append({"player_id": pl_id, 'start_date': str(sd), 'end_date': str(ed), 'parameter_id': k,
                                'value': calc_dict[k], "date_created": date.today(), "source": 'webforms_calc',
                                'parametertree_id': 52})
        dff = pd.DataFrame(required_df)
        print(dff)
        self.InsertORUpdate(dff)

    def calc_script_meatMarketPlace(self, pl_id, sd, ed):
        calc_dict = {}
        for i in range(1, 4000):
            calc_dict[i] = 0
        try:
            d = self.par_val_dict(pl_id, sd, ed)
        except:
            pass

        try:
            calc_dict[1501] = (d[1499] * d[1500] * self.month_range(sd)) / 10000
        except:
            pass
        calc_dict[1507] = 100 - (d[1502] + d[1503] + d[1504] + d[1505] + d[1506])
        calc_dict[1513] = 100 - (d[1508] + d[1509] + d[1510] + d[1511] + d[1512])

        required_df = []
        for k in calc_dict:
            if calc_dict[k] == 0:
                continue
            print(k, calc_dict[k])
            required_df.append({"player_id": pl_id, 'start_date': str(sd), 'end_date': str(ed), 'parameter_id': k,
                                'value': calc_dict[k], "date_created": date.today(), "source": 'webforms_calc',
                                'parametertree_id': 52})
        dff = pd.DataFrame(required_df)
        print(dff)
        self.InsertORUpdate(dff)

    def calc_script_d2c(self, pl_id, sd, ed):
        calc_dict = {}
        for i in range(1, 4000):
            calc_dict[i] = 0
        try:
            d = self.par_val_dict(pl_id, sd, ed)
        except:
            pass

        try:
            calc_dict[243] = d[454] + d[455] + d[456] + d[453]
            calc_dict[244] = d[245] + d[246]
            calc_dict[247] = (calc_dict[243] * (100 - calc_dict[244])) / 100
            calc_dict[241] = (calc_dict[243] / d[242]) * 100
        except:
            pass
        try:
            calc_dict[286] = 100 - d[287]
        except:
            pass
        try:
            calc_dict[221] = 100 - d[222]
        except:
            pass
        try:
            calc_dict[478] = 100 - (d[476] + d[477])
        except:
            pass

        try:
            calc_dict[227] = (d[241] * d[476]) / 100
        except:
            pass
        try:
            calc_dict[228] = (d[241] * d[477]) / 100
        except:
            pass
        try:
            calc_dict[229] = d[241] - calc_dict[227] - calc_dict[228]
        except:
            pass
        try:
            calc_dict[461] = (d[453] / d[469]) * 10000
        except:
            pass
        try:
            calc_dict[462] = (d[454] / d[471]) * 10000
        except:
            pass
        try:
            calc_dict[463] = (d[455] / d[470]) * 10000
        except:
            pass
        try:
            calc_dict[464] = (d[456] / d[472]) * 10000
        except:
            pass

        try:
            calc_dict[460] = calc_dict[461] + calc_dict[462] + calc_dict[463] + calc_dict[464]
        except:
            pass

        try:
            calc_dict[468] = (calc_dict[243] / calc_dict[460]) * 10000
        except:
            pass
        try:
            calc_dict[519] = d[240] / calc_dict[468]
        except:
            pass
        try:
            calc_dict[239] = (d[241] / d[240]) * 10
        except:
            pass

        try:
            calc_dict[1332] = calc_dict[239] / d[238]
        except:
            pass

        required_df = []
        for k in calc_dict:
            if calc_dict[k] == 0:
                continue
            print(k, calc_dict[k])
            required_df.append({"player_id": pl_id, 'start_date': str(sd), 'end_date': str(ed), 'parameter_id': k,
                                'value': calc_dict[k], "date_created": date.today(), "source": 'webforms_calc',
                                'parametertree_id': 52})
        dff = pd.DataFrame(required_df)
        print(dff)
        self.InsertORUpdate(dff)

    def calc_script_edtech(self, pl_id, sd, ed):
        calc_dict = {}
        for i in range(1, 4000):
            calc_dict[i] = 0
        try:
            d = self.par_val_dict(pl_id, sd, ed)
        except:
            pass

        calc_dict[918] = d[919] + d[920]
        calc_dict[921] = d[922] + d[923]
        calc_dict[924] = d[925] + d[926] + d[927]
        calc_dict[917] = calc_dict[918] + calc_dict[921] + calc_dict[924]
        calc_dict[916] = calc_dict[917] + calc_dict[928]
        calc_dict[928] = d[929] + d[930] + d[931]
        calc_dict[2404] = d[2403] - d[2405]
        calc_dict[2407] = d[2406] - d[2408]
        calc_dict[970] = d[972] + d[973]
        calc_dict[956] = d[957] + d[958]
        calc_dict[959] = d[960] + d[961]
        calc_dict[962] = d[963] + d[964] + d[965]
        calc_dict[966] = d[967] + d[968] + d[969]
        calc_dict[976] = d[977] + d[978]
        calc_dict[979] = d[980] + d[981]
        calc_dict[982] = d[983] + d[984] + d[985]
        calc_dict[986] = d[987] + d[988] + d[989]
        calc_dict[2414] = 100 - (d[2412] + d[2413])
        try:
            calc_dict[2420] = (d[2419] / d[2415]) * 100
        except:
            pass
        calc_dict[2432] = d[2433] + d[2434] + d[2435] + d[2436]
        calc_dict[2409] = 100 - (d[2403] + d[2406])
        calc_dict[2410] = calc_dict[2409] - d[2408]
        calc_dict[975] = calc_dict[976] + calc_dict[979] + calc_dict[982]
        calc_dict[955] = calc_dict[956] + calc_dict[959] + calc_dict[962]
        try:
            calc_dict[949] = (calc_dict[975] / calc_dict[955]) * 10000
        except:
            pass
        try:
            calc_dict[950] = (calc_dict[976] / calc_dict[956]) * 10000
        except:
            pass
        try:
            calc_dict[951] = (calc_dict[979] / calc_dict[959]) * 10000
        except:
            pass
        try:
            calc_dict[952] = (calc_dict[982] / calc_dict[962]) * 10000
        except:
            pass
        try:
            calc_dict[953] = (calc_dict[986] / calc_dict[966]) * 10000
        except:
            pass

        required_df = []
        for k in calc_dict:
            if calc_dict[k] == 0:
                continue
            print(k, calc_dict[k])
            required_df.append({"player_id": pl_id, 'start_date': str(sd), 'end_date': str(ed), 'parameter_id': k,
                                'value': calc_dict[k], "date_created": date.today(), "source": 'webforms_calc',
                                'parametertree_id': 52})
        dff = pd.DataFrame(required_df)
        print(dff)
        self.InsertORUpdate(dff)

    def calc_script_mobility(self, pl_id, sd, ed):
        calc_dict = {}
        for i in range(1, 4000):
            calc_dict[i] = 0
        try:
            d = self.par_val_dict(pl_id, sd, ed)
        except:
            pass

        calc_dict[1971] = d[1972] + d[2070] + d[2084]
        calc_dict[1973] = (d[1974] / d[1972]) / 100
        calc_dict[1975] = (d[1976] / d[1972]) / 100
        calc_dict[1977] = d[1972] - calc_dict[1974] - calc_dict[1975]
        calc_dict[1978] = (calc_dict[1977] / d[1972]) * 100
        calc_dict[1980] = (d[1979] / d[1972]) * 100
        calc_dict[1982] = (d[1981] / d[1972]) * 100
        calc_dict[1984] = (d[1983] / d[1972]) * 100
        calc_dict[1985] = d[1972] - d[1979] - d[1981] - d[1983]
        calc_dict[1986] = (calc_dict[1985] / d[1972]) * 100
        calc_dict[1988] = (d[1987] / d[1972]) * 100
        calc_dict[1990] = (d[1989] / d[1972]) * 100
        calc_dict[1991] = d[1972] - d[1987] - d[1989]
        try:
            calc_dict[1992] = (calc_dict[1991] / d[1972]) * 100
        except:
            pass
        try:
            calc_dict[1997] = (calc_dict[1985] / d[1972]) * 100
        except:
            pass
        calc_dict[2002] = 100 - d[1999] - d[2000] - d[2001]
        calc_dict[2011] = 100 - d[2008] - d[2009] - d[2010]
        calc_dict[2020] = 100 - d[2017] - d[2018] - d[2019]
        calc_dict[2029] = 100 - d[2026] - d[2027] - d[2028]
        calc_dict[2038] = 100 - d[2035] - d[2036] - d[2037]
        calc_dict[2047] = 100 - d[2044] - d[2045] - d[2046]
        calc_dict[2056] = 100 - d[2053] - d[2054] - d[2055]
        calc_dict[1997] = d[1994] - d[1995] - d[1996]
        calc_dict[2006] = d[2003] - d[2004] - d[2005]
        calc_dict[2015] = d[2012] - d[2013] - d[2014]
        calc_dict[2024] = d[2021] - d[2022] - d[2023]
        calc_dict[2033] = d[2030] - d[2031] - d[2032]
        calc_dict[2042] = d[2039] - d[2040] - d[2041]
        calc_dict[2051] = d[2048] - d[2049] - d[2050]
        calc_dict[2069] = d[1972] - (
                    d[2057] + d[2058] + d[2059] + d[2060] + d[2061] + d[2062] + d[2063] + d[2064] + d[2065] + d[2066] +
                    d[2067] + d[2068])
        calc_dict[2083] = d[2070] - (
                    d[2071] + d[2072] + d[2073] + d[2074] + d[2075] + d[2076] + d[2077] + d[2078] + d[2079] + d[2080] +
                    d[2081] + d[2082])
        calc_dict[2114] = d[2084] - (
                    d[2085] + d[2086] + d[2087] + d[2088] + d[2089] + d[2090] + d[2091] + d[2092] + d[2093] + d[2094] +
                    d[2095] + d[2096]
                    + d[2097] + d[2098] + d[2099] + d[2100] + d[2101] + d[2102] + d[2103] + d[2104] + d[2105] + d[
                        2106] + d[2107] + d[2108]
                    + d[2109] + d[2110] + d[2111] + d[2112] + d[2113])
        calc_dict[2115] = d[2116] + d[2214] + d[2228]
        try:
            calc_dict[2118] = (d[2117] / d[2116]) * 100
        except:
            pass
        try:
            calc_dict[2120] = (d[2119] / d[2116]) * 100
        except:
            pass
        calc_dict[2121] = d[2116] - d[2117] - d[2119]
        try:
            calc_dict[2122] = (calc_dict[2121] / d[2116]) * 100
        except:
            pass
        try:
            calc_dict[2124] = (d[2123] / d[2116]) * 100
        except:
            pass
        try:
            calc_dict[2126] = (d[2125] / d[2116]) * 100
        except:
            pass
        try:
            calc_dict[2128] = (d[2127] / d[2116]) * 100
        except:
            pass
        calc_dict[2129] = d[2116] - d[2123] - d[2125] - d[2127]
        try:
            calc_dict[2130] = (calc_dict[2129] / d[2116]) * 100
        except:
            pass
        try:
            calc_dict[2132] = (d[2131] / d[2116]) * 100
        except:
            pass
        try:
            calc_dict[2134] = (d[2133] / d[2116]) * 100
        except:
            pass
        calc_dict[2135] = d[2116] - d[2131] - d[2133]
        try:
            calc_dict[2136] = (calc_dict[2135] / d[2116]) * 100
        except:
            pass
        calc_dict[2141] = d[2138] - d[2139] - d[2140]
        calc_dict[2150] = d[2147] - d[2148] - d[2149]
        calc_dict[2159] = d[2156] - d[2157] - d[2158]
        calc_dict[2168] = d[2165] - d[2166] - d[2167]
        calc_dict[2177] = d[2174] - d[2175] - d[2176]
        calc_dict[2186] = d[2183] - d[2184] - d[2185]
        calc_dict[2146] = 100 - d[2143] - d[2144] - d[2145]
        calc_dict[2155] = 100 - d[2152] - d[2153] - d[2154]
        calc_dict[2164] = 100 - d[2161] - d[2162] - d[2163]
        calc_dict[2173] = 100 - d[2170] - d[2171] - d[2172]
        calc_dict[2182] = 100 - d[2179] - d[2180] - d[2181]
        calc_dict[2191] = 100 - d[2188] - d[2189] - d[2190]
        calc_dict[2200] = 100 - d[2197] - d[2198] - d[2199]
        calc_dict[2213] = d[2116] - (
                    d[2201] + d[2202] + d[2203] + d[2204] + d[2205] + d[2206] + d[2207] + d[2208] + d[2209] + d[2210] +
                    d[2211] + d[2212])
        calc_dict[2227] = d[2214] - (
                    d[2215] + d[2216] + d[2217] + d[2218] + d[2219] + d[2220] + d[2221] + d[2222] + d[2223] + d[2224] +
                    d[2225] + d[2226])
        calc_dict[2258] = d[2228] - (
                    d[2229] + d[2230] + d[2231] + d[2232] + d[2233] + d[2234] + d[2235] + d[2236] + d[2237] + d[2238] +
                    d[2239] + d[2240]
                    + d[2241] + d[2242] + d[2243] + d[2244] + d[2245] + d[2246] + d[2247] + d[2248] + d[2249] + d[
                        2250] + d[2251] + d[2252]
                    + d[2253] + d[2254] + d[2255] + d[2256] + d[2257])
        try:
            calc_dict[2259] = calc_dict[2115] / calc_dict[1971]
        except:
            pass
        try:
            calc_dict[2260] = d[2116] / d[1972]
        except:
            pass
        try:
            calc_dict[2261] = d[2117] / calc_dict[1973]
        except:
            pass
        try:
            calc_dict[2262] = calc_dict[2118] / d[1974]
        except:
            pass
        try:
            calc_dict[2263] = d[2119] / calc_dict[1975]
        except:
            pass
        try:
            calc_dict[2264] = calc_dict[2120] / d[1976]
        except:
            pass
        try:
            calc_dict[2265] = calc_dict[2121] / calc_dict[1977]
        except:
            pass
        try:
            calc_dict[2266] = calc_dict[2122] / calc_dict[1978]
        except:
            pass
        try:
            calc_dict[2267] = d[2123] / d[1979]
        except:
            pass
        try:
            calc_dict[2268] = calc_dict[2124] / calc_dict[1980]
        except:
            pass
        try:
            calc_dict[2269] = d[2125] / d[1981]
        except:
            pass
        try:
            calc_dict[2270] = calc_dict[2126] / calc_dict[1982]
        except:
            pass
        try:
            calc_dict[2271] = d[2127] / d[1983]
        except:
            pass
        try:
            calc_dict[2272] = calc_dict[2128] / calc_dict[1984]
        except:
            pass
        try:
            calc_dict[2273] = calc_dict[2129] / calc_dict[1985]
        except:
            pass
        try:
            calc_dict[2274] = calc_dict[2130] / calc_dict[1986]
        except:
            pass
        try:
            calc_dict[2275] = d[2131] / d[1987]
        except:
            pass
        try:
            calc_dict[2276] = calc_dict[2132] / calc_dict[1988]
        except:
            pass
        try:
            calc_dict[2277] = d[2133] / d[1989]
        except:
            pass
        try:
            calc_dict[2278] = calc_dict[2134] / calc_dict[1990]
        except:
            pass
        try:
            calc_dict[2279] = calc_dict[2135] / calc_dict[1991]
        except:
            pass
        try:
            calc_dict[2280] = calc_dict[2136] / calc_dict[1992]
        except:
            pass
        try:
            calc_dict[2281] = d[2137] / d[1993]
        except:
            pass
        try:
            calc_dict[2282] = d[2138] / d[1994]
        except:
            pass
        try:
            calc_dict[2283] = d[2139] / d[1995]
        except:
            pass
        try:
            calc_dict[2284] = d[2140] / d[1996]
        except:
            pass
        try:
            calc_dict[2285] = calc_dict[2141] / calc_dict[1997]
        except:
            pass
        try:
            calc_dict[2286] = d[2142] / d[1998]
        except:
            pass
        try:
            calc_dict[2287] = d[2143] / d[1999]
        except:
            pass
        try:
            calc_dict[2288] = d[2144] / d[2000]
        except:
            pass
        try:
            calc_dict[2289] = d[2145] / d[2001]
        except:
            pass
        try:
            calc_dict[2290] = calc_dict[2146] / calc_dict[2002]
        except:
            pass
        try:
            calc_dict[2291] = d[2147] / d[2003]
        except:
            pass
        try:
            calc_dict[2292] = d[2148] / d[2004]
        except:
            pass
        try:
            calc_dict[2293] = d[2149] / d[2005]
        except:
            pass
        try:
            calc_dict[2294] = calc_dict[2150] / calc_dict[2006]
        except:
            pass
        try:
            calc_dict[2295] = d[2151] / d[2007]
        except:
            pass
        try:
            calc_dict[2296] = d[2152] / d[2008]
        except:
            pass
        try:
            calc_dict[2297] = d[2153] / d[2009]
        except:
            pass
        try:
            calc_dict[2298] = d[2154] / d[2010]
        except:
            pass
        try:
            calc_dict[2299] = calc_dict[2155] / calc_dict[2011]
        except:
            pass
        try:
            calc_dict[2300] = d[2156] / d[2012]
        except:
            pass
        try:
            calc_dict[2301] = d[2157] / d[2013]
        except:
            pass
        try:
            calc_dict[2302] = d[2158] / d[2014]
        except:
            pass
        try:
            calc_dict[2303] = calc_dict[2159] / calc_dict[2015]
        except:
            pass
        try:
            calc_dict[2304] = d[2160] / d[2016]
        except:
            pass
        try:
            calc_dict[2305] = d[2161] / d[2017]
        except:
            pass
        try:
            calc_dict[2306] = d[2162] / d[2018]
        except:
            pass
        try:
            calc_dict[2307] = d[2163] / d[2019]
        except:
            pass
        try:
            calc_dict[2308] = calc_dict[2164] / calc_dict[2020]
        except:
            pass
        try:
            calc_dict[2309] = d[2165] / d[2021]
        except:
            pass
        try:
            calc_dict[2310] = d[2166] / d[2022]
        except:
            pass
        try:
            calc_dict[2311] = d[2167] / d[2023]
        except:
            pass
        try:
            calc_dict[2312] = calc_dict[2168] / calc_dict[2024]
        except:
            pass
        try:
            calc_dict[2313] = d[2169] / d[2025]
        except:
            pass
        try:
            calc_dict[2314] = d[2170] / d[2026]
        except:
            pass
        try:
            calc_dict[2315] = d[2171] / d[2027]
        except:
            pass
        try:
            calc_dict[2316] = d[2172] / d[2028]
        except:
            pass
        try:
            calc_dict[2317] = calc_dict[2173] / calc_dict[2029]
        except:
            pass
        try:
            calc_dict[2318] = d[2174] / d[2030]
        except:
            pass
        try:
            calc_dict[2319] = d[2175] / d[2031]
        except:
            pass
        try:
            calc_dict[2320] = d[2176] / d[2032]
        except:
            pass
        try:
            calc_dict[2321] = calc_dict[2177] / calc_dict[2033]
        except:
            pass
        try:
            calc_dict[2322] = d[2178] / d[2034]
        except:
            pass
        try:
            calc_dict[2323] = d[2179] / d[2035]
        except:
            pass
        try:
            calc_dict[2324] = d[2180] / d[2036]
        except:
            pass
        try:
            calc_dict[2325] = d[2181] / d[2037]
        except:
            pass
        try:
            calc_dict[2326] = calc_dict[2182] / calc_dict[2038]
        except:
            pass
        try:
            calc_dict[2327] = d[2183] / d[2039]
        except:
            pass
        try:
            calc_dict[2328] = d[2184] / d[2040]
        except:
            pass
        try:
            calc_dict[2329] = d[2185] / d[2041]
        except:
            pass
        try:
            calc_dict[2330] = calc_dict[2186] / calc_dict[2042]
        except:
            pass
        try:
            calc_dict[2331] = d[2187] / d[2043]
        except:
            pass
        try:
            calc_dict[2332] = d[2188] / d[2044]
        except:
            pass
        try:
            calc_dict[2333] = d[2189] / d[2045]
        except:
            pass
        try:
            calc_dict[2334] = d[2190] / d[2046]
        except:
            pass
        try:
            calc_dict[2335] = calc_dict[2191] / calc_dict[2047]
        except:
            pass
        try:
            calc_dict[2336] = d[2192] / d[2048]
        except:
            pass
        try:
            calc_dict[2337] = d[2193] / d[2049]
        except:
            pass
        try:
            calc_dict[2338] = d[2194] / d[2050]
        except:
            pass
        try:
            calc_dict[2339] = d[2195] / calc_dict[2051]
        except:
            pass
        try:
            calc_dict[2340] = d[2196] / d[2052]
        except:
            pass
        try:
            calc_dict[2341] = d[2197] / d[2053]
        except:
            pass
        try:
            calc_dict[2342] = d[2198] / d[2054]
        except:
            pass
        try:
            calc_dict[2343] = d[2199] / d[2055]
        except:
            pass
        try:
            calc_dict[2344] = calc_dict[2200] / calc_dict[2056]
        except:
            pass
        try:
            calc_dict[2345] = d[2201] / d[2057]
        except:
            pass
        try:
            calc_dict[2346] = d[2202] / d[2058]
        except:
            pass
        try:
            calc_dict[2347] = d[2203] / d[2059]
        except:
            pass
        try:
            calc_dict[2348] = d[2204] / d[2060]
        except:
            pass
        try:
            calc_dict[2349] = d[2205] / d[2061]
            calc_dict[2350] = d[2206] / d[2062]
            calc_dict[2351] = d[2207] / d[2063]
            calc_dict[2352] = d[2208] / d[2064]
            calc_dict[2353] = d[2209] / d[2065]
            calc_dict[2354] = d[2210] / d[2066]
            calc_dict[2355] = d[2211] / d[2067]
            calc_dict[2356] = d[2212] / d[2068]
            calc_dict[2357] = calc_dict[2213] / calc_dict[2069]
            calc_dict[2358] = d[2214] / d[2070]
            calc_dict[2359] = d[2215] / d[2071]
            calc_dict[2360] = d[2216] / d[2072]
            calc_dict[2361] = d[2217] / d[2073]
            calc_dict[2362] = d[2218] / d[2074]
            calc_dict[2363] = d[2219] / d[2075]
            calc_dict[2364] = d[2220] / d[2076]
            calc_dict[2365] = d[2221] / d[2077]
            calc_dict[2366] = d[2222] / d[2078]
            calc_dict[2367] = d[2223] / d[2079]
            calc_dict[2368] = d[2224] / d[2080]
            calc_dict[2369] = d[2225] / d[2081]
            calc_dict[2370] = d[2226] / d[2082]
            calc_dict[2371] = calc_dict[2227] / calc_dict[2083]
            calc_dict[2372] = d[2228] / d[2084]
            calc_dict[2373] = d[2229] / d[2085]
            calc_dict[2374] = d[2230] / d[2086]
            calc_dict[2375] = d[2231] / d[2087]
            calc_dict[2376] = d[2232] / d[2088]
            calc_dict[2377] = d[2233] / d[2089]
            calc_dict[2378] = d[2234] / d[2090]
            calc_dict[2379] = d[2235] / d[2091]
            calc_dict[2380] = d[2236] / d[2092]
            calc_dict[2381] = d[2237] / d[2093]
            calc_dict[2382] = d[2238] / d[2094]
            calc_dict[2383] = d[2239] / d[2095]
            calc_dict[2384] = d[2240] / d[2096]
            calc_dict[2385] = d[2241] / d[2097]
            calc_dict[2386] = d[2242] / d[2098]
            calc_dict[2387] = d[2243] / d[2099]
            calc_dict[2388] = d[2244] / d[2100]
            calc_dict[2389] = d[2245] / d[2101]
            calc_dict[2390] = d[2246] / d[2102]
            calc_dict[2391] = d[2247] / d[2103]
            calc_dict[2392] = d[2248] / d[2104]
            calc_dict[2393] = d[2249] / d[2105]
            calc_dict[2394] = d[2250] / d[2106]
            calc_dict[2395] = d[2251] / d[2107]
            calc_dict[2396] = d[2252] / d[2108]
            calc_dict[2397] = d[2253] / d[2109]
            calc_dict[2398] = d[2254] / d[2110]
            calc_dict[2399] = d[2255] / d[2111]
            calc_dict[2400] = d[2256] / d[2112]
            calc_dict[2401] = d[2257] / d[2113]
            calc_dict[2402] = calc_dict[2258] / calc_dict[2114]
        except:
            pass

        required_df = []
        for k in calc_dict:
            if calc_dict[k] == 0:
                continue
            print(k, calc_dict[k])
            required_df.append({"player_id": pl_id, 'start_date': str(sd), 'end_date': str(ed), 'parameter_id': k,
                                'value': calc_dict[k], "date_created": date.today(), "source": 'webforms_calc',
                                'parametertree_id': 52})
        dff = pd.DataFrame(required_df)
        print(dff)
        self.InsertORUpdate(dff)

    def calc_script_horizontals(self, pl_id, sd, ed):
        calc_dict = {}
        for i in range(1, 4000):
            calc_dict[i] = 0
        try:
            d = self.par_val_dict(pl_id, sd, ed)
        except:
            pass
        try:
            calc_dict[2757] = 100 - d[2756]
        except:
            pass
        try:
            calc_dict[2760] = 100 - d[2759]
        except:
            pass
        try:
            calc_dict[2762] = (d[238] / d[52]) * 100
        except:
            pass
        try:
            calc_dict[1419] = (d[238] / d[52]) * 100
        except:
            pass
        try:
            calc_dict[239] = d[241] / d[240]
        except:
            pass
        try:
            calc_dict[2769] = calc_dict[239] / d[238]
        except:
            pass
        try:
            calc_dict[243] = d[241] * (100 - d[242])
        except:
            pass
        try:
            calc_dict[244] = d[245] + d[246]
        except:
            pass
        try:
            calc_dict[247] = calc_dict[243] * (100 - calc_dict[244])
        except:
            pass
        try:
            calc_dict[461] = d[453] / d[469]
        except:
            pass
        try:
            calc_dict[462] = d[454] / d[470]
        except:
            pass
        try:
            calc_dict[463] = d[455] / d[471]
        except:
            pass
        try:
            calc_dict[464] = d[456] / d[472]
        except:
            pass
        try:
            calc_dict[465] = d[457] / d[473]
        except:
            pass
        try:
            calc_dict[618] = d[554] / d[1359]
        except:
            pass
        try:
            calc_dict[1558] = (d[1537] / d[1360]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[1559] = (d[1538] / d[1361]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[1560] = (d[1539] / d[1362]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[1561] = (d[1540] / d[1363]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[1562] = (d[1541] / d[1364]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[1563] = (d[1542] / d[1365]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[1564] = (d[1543] / d[1366]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[1565] = (d[1544] / d[1367]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[1566] = (d[1545] / d[1368]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[1567] = (d[1546] / d[1369]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[1572] = (d[1551] / d[514]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[623] = (d[559] / d[654]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[1568] = (d[1547] / d[1370]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[2851] = (d[2855] / d[1371]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[2852] = (d[2856] / d[1372]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[1571] = (d[1550] / d[1373]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[2853] = (d[2857] / d[1422]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[2854] = (d[2858] / d[1423]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[626] = (d[562] / d[1374]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[1573] = (d[1552] / d[1375]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[1574] = (d[1553] / d[1376]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[1575] = (d[1554] / d[1377]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[1576] = (d[1555] / d[1378]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[466] = (d[458] / d[474]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[2799] = (d[2771] / d[2806]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[631] = (d[426] / d[499]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[634] = (d[428] / d[502]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[635] = (d[429] / d[503]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[633] = (d[425] / d[498]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[467] = (d[459] / d[479]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[2800] = (d[2773] / d[2810]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[646] = (d[584] / d[2811]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[2801] = (d[2774] / d[2812]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[640] = (d[580] / d[1379]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[2802] = (d[2776] / d[2813]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[256] = (d[250] / d[2814]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[643] = (d[581] / d[301]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[527] = (d[524] / d[526]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[1563] = (d[1542] / d[1365]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[2804] = (d[2777] / d[2815]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[2805] = (d[2778] / d[2816]) / 10 ** 4
        except:
            pass
        try:
            calc_dict[2819] = 100 - (d[2817] + d[2818])
        except:
            pass
        try:
            calc_dict[225] = 100 - (d[223] + d[224] + d[226])
        except:
            pass
        try:
            calc_dict[1411] = 100 - (d[1409] + d[1410] + d[1412])
        except:
            pass
        try:
            calc_dict[221] = 100 - d[222]
        except:
            pass
        try:
            calc_dict[1418] = calc_dict[243] - (d[1413] + d[1414] + d[1415] + d[1416] + d[1417])
        except:
            pass
        try:
            calc_dict[2829] = 100 - d[2828]
        except:
            pass
        try:
            calc_dict[2831] = 100 - d[2830]
        except:
            pass
        try:
            calc_dict[2833] = 100 - d[2832]
        except:
            pass
        try:
            calc_dict[460] = calc_dict[461] + calc_dict[462] + calc_dict[463] + calc_dict[464] + calc_dict[465] + \
                             calc_dict[623] + calc_dict[626] + calc_dict[466] + calc_dict[467] + calc_dict[640] + \
                             calc_dict[643] + calc_dict[527]
        except:
            pass
        try:
            calc_dict[468] = calc_dict[243] / calc_dict[460]
        except:
            pass
        try:
            calc_dict[2770] = d[240] / calc_dict[460]
        except:
            pass
        try:
            calc_dict[227] = d[2817] / calc_dict[241]
        except:
            pass
        try:
            calc_dict[228] = d[2818] / calc_dict[241]
        except:
            pass
        try:
            calc_dict[229] = calc_dict[2819] / calc_dict[241]
        except:
            pass
        try:
            calc_dict[213] = calc_dict[239] / self.month_range(sd)
        except:
            pass

        print(calc_dict)

        required_df = []
        for k in calc_dict:
            if calc_dict[k] == 0:
                continue
            print(k, calc_dict[k])
            required_df.append({"player_id": pl_id, 'start_date': str(sd), 'end_date': str(ed), 'parameter_id': k,
                                'value': calc_dict[k], "date_created": date.today(), "source": 'webforms_calc',
                                'parametertree_id': 52})
        dff = pd.DataFrame(required_df)
        print(dff)
        self.InsertORUpdate(dff)

    def calc_script_ehealth(self, pl_id, sd, ed):
        calc_dict = {}
        for i in range(1, 4000):
            calc_dict[i] = 0
        try:
            d = self.par_val_dict(pl_id, sd, ed)
            print(d)
        except:
            pass
        try:
            calc_dict[1751] = 100 - d[1752]
        except:
            pass
        try:
            calc_dict[1755] = 100 - (d[1753] + d[1754])
        except:
            pass
        try:
            calc_dict[1762] = 100 - (d[1757] + d[1758] + d[1759] + d[1760] + d[1761])
        except:
            pass
        try:
            calc_dict[884] = d[1763] + d[1764]
        except:
            pass
        try:
            calc_dict[1849] = (d[1848] / d[1846]) * 100
        except:
            pass
        try:
            calc_dict[1853] = 100 - (d[1851] + d[1852])
        except:
            pass
        try:
            calc_dict[1854] = 100 - d[1855]
        except:
            pass
        try:
            calc_dict[1910] = 100 - (d[1908] + d[1909])
        except:
            pass
        try:
            calc_dict[1919] = 100 - (d[1917] + d[1918])
        except:
            pass
        try:
            calc_dict[1938] = 100 - (d[1936] + d[1937])
        except:
            pass
        try:
            calc_dict[1949] = 100 - d[1950]
        except:
            pass
        try:
            calc_dict[1968] = 100 - d[1967]
        except:
            pass
        try:
            calc_dict[1803] = d[1705] * d[1782]
        except:
            pass
        try:
            calc_dict[1804] = d[1756] * d[1783]
        except:
            pass
        try:
            calc_dict[1805] = d[882] * d[1784]
        except:
            pass
        try:
            calc_dict[1806] = d[883] * d[1785]
        except:
            pass
        try:
            calc_dict[1807] = calc_dict[884] * d[1786]
        except:
            pass
        try:
            calc_dict[1808] = d[1763] * d[1787]
        except:
            pass
        try:
            calc_dict[1809] = d[1764] * d[1788]
        except:
            pass
        try:
            calc_dict[1810] = d[885] * d[1789]
        except:
            pass
        try:
            calc_dict[1811] = d[1765] * d[1790]
        except:
            pass
        try:
            calc_dict[1791] = d[1750] * d[1766]
        except:
            pass
        try:
            calc_dict[1794] = 100 - (d[1792] + d[1793])
        except:
            pass
        try:
            calc_dict[1795] = d[1756] * d[1767]
        except:
            pass
        try:
            calc_dict[1796] = d[882] * d[1768]
        except:
            pass
        try:
            calc_dict[1797] = d[883] * d[1769]
        except:
            pass
        try:
            calc_dict[1798] = calc_dict[884] * d[1770]
        except:
            pass
        try:
            calc_dict[1799] = d[1763] * d[1771]
        except:
            pass
        try:
            calc_dict[1800] = d[1764] * d[1772]
        except:
            pass
        try:
            calc_dict[1801] = d[885] * d[1773]
        except:
            pass
        try:
            calc_dict[1802] = d[1765] * d[1774]
        except:
            pass
        try:
            calc_dict[1814] = d[1750] - (d[1750] * d[1812])
        except:
            pass
        try:
            calc_dict[905] = d[1756] - (d[1756] * d[899])
        except:
            pass
        try:
            calc_dict[906] = d[882] - (d[882] * d[900])
        except:
            pass
        try:
            calc_dict[907] = d[883] - (d[883] * d[901])
        except:
            pass
        try:
            calc_dict[908] = calc_dict[884] - (calc_dict[884] * d[902])
        except:
            pass
        try:
            calc_dict[909] = d[885] - (d[885] * d[903])
        except:
            pass
        try:
            calc_dict[1817] = d[1765] - (d[1765] * d[1813])
        except:
            pass
        try:
            calc_dict[1818] = calc_dict[1791] - (calc_dict[1791] * d[1812])
        except:
            pass
        try:
            calc_dict[1819] = calc_dict[1795] - (calc_dict[1795] * d[899])
        except:
            pass
        try:
            calc_dict[1820] = calc_dict[1796] - (calc_dict[1796] * d[900])
        except:
            pass
        try:
            calc_dict[1821] = calc_dict[1797] - (calc_dict[1797] * d[901])
        except:
            pass
        try:
            calc_dict[1822] = calc_dict[1798] - (calc_dict[1798] * d[902])
        except:
            pass
        try:
            calc_dict[1825] = calc_dict[1801] - (calc_dict[1801] * d[903])
        except:
            pass
        try:
            calc_dict[1826] = calc_dict[1802] - (calc_dict[1802] * d[1813])
        except:
            pass
        try:
            calc_dict[1827] = calc_dict[1803] - (calc_dict[1803] * d[1812])
        except:
            pass
        try:
            calc_dict[1828] = calc_dict[1804] - (calc_dict[1804] * d[899])
        except:
            pass
        try:
            calc_dict[1829] = calc_dict[1805] - (calc_dict[1805] * d[900])
        except:
            pass
        try:
            calc_dict[1830] = calc_dict[1806] - (calc_dict[1806] * d[901])
        except:
            pass
        try:
            calc_dict[1831] = calc_dict[1807] - (calc_dict[1807] * d[902])
        except:
            pass
        try:
            calc_dict[1834] = calc_dict[1810] - (calc_dict[1810] * d[903])
        except:
            pass
        try:
            calc_dict[1835] = calc_dict[1811] - (calc_dict[1811] * d[1813])
        except:
            pass
        try:
            calc_dict[1871] = (d[1864] * calc_dict[1827]) / 7
        except:
            pass
        try:
            calc_dict[1872] = (d[1865] * calc_dict[1828]) / 7
        except:
            pass
        try:
            calc_dict[1873] = (d[1866] * calc_dict[1829]) / 7
        except:
            pass
        try:
            calc_dict[1874] = (d[1867] * calc_dict[1830]) / 7
        except:
            pass
        try:
            calc_dict[1875] = (d[1868] * calc_dict[1831]) / 7
        except:
            pass
        try:
            calc_dict[1876] = (d[1869] * calc_dict[1834]) / 7
        except:
            pass
        try:
            calc_dict[1877] = (d[1870] * calc_dict[1835]) / 7
        except:
            pass
        try:
            calc_dict[1878] = calc_dict[1874] + calc_dict[1876]
        except:
            pass
        try:
            calc_dict[1880] = d[1881] + d[1882] + d[1883] + d[1884]
        except:
            pass
        try:
            calc_dict[1885] = (calc_dict[1871] + d[93] + calc_dict[1879]) * 7 - calc_dict[1880]
        except:
            pass
        try:
            calc_dict[1887] = calc_dict[1885] - d[1886]
        except:
            pass
        try:
            calc_dict[1893] = calc_dict[1887] - (d[1888] + d[1889] + d[1890] + d[1891] + d[1892])
        except:
            pass

        required_df = []
        for k in calc_dict:
            if calc_dict[k] == 0:
                continue
            print(k, calc_dict[k])
            required_df.append({"player_id": pl_id, 'start_date': str(sd), 'end_date': str(ed), 'parameter_id': k,
                                'value': calc_dict[k], "date_created": date.today(), "source": 'webforms_calc',
                                'parametertree_id': 52})
        dff = pd.DataFrame(required_df)
        self.InsertORUpdate(dff)

    def calc_script_foodtech(self, pl_id, sd, ed):
        calc_dict = {}
        for i in range(1, 4000):
            calc_dict[i] = 0
        try:
            d = self.par_val_dict(pl_id, sd, ed)
        except:
            pass
        try:
            calc_dict[340]=d[336]-(d[337]+d[338]+d[339])
        except:
            pass
        try:
            calc_dict[1602]=d[1599]-(d[1600]+d[1601])
        except:
            pass
        try:
            calc_dict[352]=d[337]*(100-d[342])
        except:
            pass
        try:
            calc_dict[353]=d[338]*(100-d[343])
        except:
            pass
        try:
            calc_dict[354]=d[339]*(100-d[344])
        except:
            pass
        try:
            calc_dict[355]=calc_dict[340]*(100-d[345])
        except:
            pass
        try:
            calc_dict[1611]=d[1599]*(100-d[1603])
        except:
            pass
        try:
            calc_dict[1612]=d[1600]*(100-d[1604])
        except:
            pass
        try:
            calc_dict[1613]=d[1601]*(100-d[1605])
        except:
            pass
        try:
            calc_dict[1614]=d[1602]*(100-d[1606])
        except:
            pass
        try:
            calc_dict[361]=((d[362]*d[337])+(d[338]*d[363])+(d[364]*d[339])+(d[365]*calc_dict[340]))/(d[337]+d[338]+d[339]+calc_dict[340])
        except:
            pass
        try:
            calc_dict[366]=((d[367]*d[337])+(d[338]*d[368])+(d[369]*d[339])+(d[370]*calc_dict[340]))/(d[337]+d[338]+d[339]+calc_dict[340])
        except:
            pass
        try:
            calc_dict[356]=calc_dict[366]-calc_dict[361]
        except:
            pass
        try:
            calc_dict[357]=d[367]-d[362]
        except:
            pass
        try:
            calc_dict[358]=d[368]-d[363]
        except:
            pass
        try:
            calc_dict[359]=d[369]-d[364]
        except:
            pass
        try:
            calc_dict[360]=d[370]-d[365]
        except:
            pass
        try:
            calc_dict[1615]=d[1623]-d[1619]
        except:
            pass
        try:
            calc_dict[1616]=d[1624]-d[1620]
        except:
            pass
        try:
            calc_dict[1617]=d[1625]-d[1621]
        except:
            pass
        try:
            calc_dict[1618]=d[1626]-d[1622]
        except:
            pass
        try:
            calc_dict[371]=month_range(sd)*d[336]*calc_dict[366]/(10**4)
        except:
            pass
        try:
            calc_dict[372]=month_range(sd)*d[337]*d[367]/(10**4)
        except:
            pass
        try:
            calc_dict[373]=month_range(sd)*d[338]*d[368]/(10**4)
        except:
            pass
        try:
            calc_dict[374]=month_range(sd)*d[339]*d[369]/(10**4)
        except:
            pass
        try:
            calc_dict[375]=calc_dict[371]-(calc_dict[372]+calc_dict[373]+calc_dict[374])
        except:
            pass
        try:
            calc_dict[1627]=month_range(sd)*d[1599]*d[1623]/(10**4)
        except:
            pass
        try:
            calc_dict[1628]=month_range(sd)*d[1600]*d[1624]/(10**4)
        except:
            pass
        try:
            calc_dict[1629]=month_range(sd)*d[1601]*d[1625]/(10**4)
        except:
            pass
        try:
            calc_dict[1630]=calc_dict[371]-(calc_dict[1627]+calc_dict[1628]+calc_dict[1629])
        except:
            pass
        try:
            calc_dict[323]=(calc_dict[372]/calc_dict[371])*100
        except:
            pass
        try:
            calc_dict[324]=(calc_dict[373]/calc_dict[371])*100
        except:
            pass
        try:
            calc_dict[325]=(calc_dict[374]/calc_dict[371])*100
        except:
            pass
        try:
            calc_dict[326]=(calc_dict[375]/calc_dict[371])*100
        except:
            pass
        try:
            calc_dict[1632]=(calc_dict[1627]/calc_dict[371])*100
        except:
            pass
        try:
            calc_dict[1633]=(calc_dict[1628]/calc_dict[371])*100
        except:
            pass
        try:
            calc_dict[1634]=(calc_dict[1629]/calc_dict[371])*100
        except:
            pass
        try:
            calc_dict[1635]=(calc_dict[1630]/calc_dict[371])*100
        except:
            pass
        try:
            calc_dict[1642]=d[1643]+d[1644]+d[1645]
        except:
            pass
        try:
            calc_dict[1665]=d[1666]+d[1667]+d[1668]
        except:
            pass
        try:
            calc_dict[1686]=(d[1663]*d[1640]*month_range(sd))/10**4
            calc_dict[1687]=d[1664]*d[1641]*month_range(sd)/10**4
            calc_dict[1688]=d[1665]*d[1642]*month_range(sd)/10**4
            calc_dict[1689]=d[1666]*d[1643]*month_range(sd)/10**4
            calc_dict[1690]=d[1667]*d[1644]*month_range(sd)/10**4
            calc_dict[1691]=d[1668]*d[1645]*month_range(sd)/10**4
            calc_dict[1692]=d[1669]*d[1646]*month_range(sd)/10**4
            calc_dict[1693]=d[1670]*d[1647]*month_range(sd)/10**4
            calc_dict[1694]=d[1671]*d[1648]*month_range(sd)/10**4
            calc_dict[1695]=d[1672]*d[1649]*month_range(sd)/10**4
            calc_dict[1696]=d[1673]*d[1650]*month_range(sd)/10**4
            calc_dict[1697]=d[1674]*d[1651]*month_range(sd)/10**4
            calc_dict[1698]=d[1675]*d[1652]*month_range(sd)/10**4
            calc_dict[1699]=d[1676]*d[1653]*month_range(sd)/10**4
            calc_dict[1700]=d[1677]*d[1654]*month_range(sd)/10**4
            calc_dict[1701]=d[1678]*d[1655]*month_range(sd)/10**4
            calc_dict[1702]=d[1679]*d[1656]*month_range(sd)/10**4
            calc_dict[1703]=d[1680]*d[1657]*month_range(sd)/10**4
            calc_dict[1704]=d[1681]*d[1658]*month_range(sd)/10**4
            calc_dict[1705]=d[1682]*d[1659]*month_range(sd)/10**4
            calc_dict[1706]=d[1683]*d[1660]*month_range(sd)/10**4
            calc_dict[1707]=d[1684]*d[1661]*month_range(sd)/10**4
            calc_dict[1708]=d[1685]*d[1662]*month_range(sd)/10**4
        except:
            pass
        try:
            calc_dict[2862]=100-d[2861]
        except:
            pass
        try:
            calc_dict[313]=100-d[312]
        except:
            pass
        try:
            calc_dict[316]=100-d[315]
        except:
            pass
        try:
            calc_dict[319]=100-d[317]
        except:
            pass
        try:
            calc_dict[322]=100-(d[320]+d[321])
        except:
            pass
        try:
            calc_dict[1710]=100-d[1709]
        except:
            pass
        try:
            calc_dict[1715]=100-(d[1712]+d[1713]+d[1714]+d[1711])
        except:
            pass
        try:
            calc_dict[1716]=100-d[1717]
        except:
            pass
        try:
            calc_dict[1720]=d[1718]-d[1719]
        except:
            pass
        try:
            calc_dict[3168]=calc_dict[1720]-d[1723]
        except:
            pass
        try:
            calc_dict[1730]=d[421]+d[422]+d[423]
        except:
            pass
        try:
            calc_dict[341]=100-(d[342]+d[343]+d[344]+d[345])
        except:
            pass
        try:
            calc_dict[351]=d[336]*(100-calc_dict[341])
        except:
            pass
        try:
            calc_dict[306]=d[336]*month_range(sd)*calc_dict[341]
        except:
            pass
        try:
            calc_dict[307]=d[336]*(100-calc_dict[341])
        except:
            pass
        try:
            calc_dict[333]=(d[336]*month_range(sd))/d[332]
        except:
            pass
        try:
            calc_dict[334]=(d[336]*month_range(sd))/d[332]*24
        except:
            pass
        try:
            calc_dict[335]=((d[336]*month_range(sd))/d[332])*d[421]
        except:
            pass
        try:
            calc_dict[1727]=d[1729]+d[417]
        except:
            pass
        try:
            calc_dict[1731]=calc_dict[1727]-calc_dict[1730]
        except:
            pass
        try:
            calc_dict[806]=calc_dict[1731]/calc_dict[1720]
        except:
            pass
        try:
            calc_dict[1332]=(d[336]*month_range(sd))/d[238]
        except:
            pass
            calc_dict[1631]=100
            
            print(calc_dict)
    
    
        required_df = []
        for k in calc_dict:
            if calc_dict[k] == 0:
                continue
            print(k, calc_dict[k])
            required_df.append({"player_id": pl_id, 'start_date': str(sd), 'end_date': str(ed), 'parameter_id': k,
                                'value': calc_dict[k], "date_created": date.today(), "source": 'webforms_calc',
                                'parametertree_id': 52})
        dff = pd.DataFrame(required_df)
        print(dff)
        self.InsertORUpdate(dff)
