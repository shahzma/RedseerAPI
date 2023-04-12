import json
import requests
import pandas as pd
from django.conf import settings
import pymysql
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from ..api_views import ReportVersionCView
# from threading import Semaphore


db_settings = settings.DATABASES['default']


class FormAutomation:
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

    def forms_release(self):
        db = pymysql.connect(
            host=db_settings['HOST'],
            port=int(db_settings['PORT']),
            user=db_settings['USER'],
            password=db_settings['PASSWORD'],
            db=db_settings['NAME'],
            ssl={'ssl': {'tls': True}}
        )
        cur = db.cursor()

        # calculate the last report version Id
        cur.execute('select * from reportversion')
        q = cur.fetchall()
        lastReportVersionId = -1
        if len(q) > 0:
            lastReportVersionId = q[-1][0]

        cur.execute("select player_name, report.id from((industry INNER JOIN report ON industry.industry_name = report.name) INNER JOIN player ON industry.industry_id = player.industry_id and player.is_active = 1);")
        playersTuples = cur.fetchall()
        playersDataframe = pd.DataFrame.from_dict(playersTuples)

        playersIndustry = dict(zip(playersDataframe[0], playersDataframe[1]))

        industryWiseData = {}
        for i in playersIndustry:
            if playersIndustry[i] not in industryWiseData:
                industryWiseData[playersIndustry[i]] = []+[i]
            else:
                industryWiseData[playersIndustry[i]
                                 ] = industryWiseData[playersIndustry[i]]+[i]

        # industryWiseDataExample = {45: [
        #     'Udaan_eFashion',
        #     'AJIO Business',
        # ],
        #     46: ['Udaan_eGrocery',
        #          'JioMart_eGrocery',
        #          'Bigbasket B2B',
        #          'Ninjacart',
        #          'Shopkirana',
        #          'Jumbotail',
        #          ],
        #     47: [
        #     'Udaan_eElectronics',
        #     'Arzoo',
        # ],
        #     48: [
        #     'Udaan_epharma',
        #     'Pharmeasy B2B',
        #     '1MG B2B'
        # ]}

        print("Form will be created for -", industryWiseData)
        url = "/formresult/1/1/"
        factory = APIRequestFactory()
        for i in industryWiseData:
            for j in industryWiseData[i]:
                lastReportVersionId += 1
                created_at = datetime.today().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                # payload = json.dumps({
                #     "name": j+' Input',
                #     "company": j,
                #     "current_instance": {
                #         "id": lastReportVersionId,
                #         "created_at": created_at,
                #     },
                #     "id": i
                # })
                # headers = {
                #     'Authorization': 'Token f810db83974e8cf8e1b0795bfdc5fcd90d8b3e6b',
                #     'Content-Type': 'application/json'
                # }
                request_data = {
                    "name": j+' Input',
                    "company": j,
                    "current_instance": {
                        "id": lastReportVersionId,
                        "created_at": created_at,
                    },
                    "id": i
                }
                try:
                    request = factory.post(url, request_data, format='json')
                    # response = requests.request(
                    #     "POST", url, headers=headers, data=payload)
                    view = ReportVersionCView.as_view()
                    response = view(request)
                    if response.status_code == 200:
                        if 'text/html' in response.headers['content-type']:
                            # if response.content_type == 'application/json':
                            response.render()
                            content = json.loads(response.content)
                            print(
                                f"Form Create success id={content['current_instance']['id']}, player={j}, created_at={content['current_instance']['created_at']}")
                        else:
                            print(
                                f"Form Create success id={content['current_instance']['id']}, player={j}, created_at={content['current_instance']['created_at']}, some error might be expected")
                    else:
                        print(
                            f"Form Create error, player={j} and report_id={i}")
                except Exception as e:
                    print(
                        f"Form Create error, player={j} and report_id={i}", e)

    def forms_auto_approve(self):
        todaysDate = datetime.now()
        monthStartDate = datetime.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0)

        # db = pymysql.connect(
        #     host=db_settings['HOST'],
        #     port=int(db_settings['PORT']),
        #     user=db_settings['USER'],
        #     password=db_settings['PASSWORD'],
        #     db=db_settings['NAME'],
        #     ssl={'ssl': {'tls': True}}
        # )
        # cur = db.cursor()
        # cur.execute(f"SELECT * FROM reportversion WHERE date_created >= '{monthStartDate}'")
        # formsTouples = cur.fetchall()
        # print("Forms", len(formsTouples), formsTouples[0])
        # cur.close()
        try:
            db_session, db_conn = self.get_db_connection()
            formsOfThisMonth = pd.read_sql(text(
                f"SELECT * FROM reportversion WHERE date_created >= '{monthStartDate}'"), db_conn)
            formsOfThisMonth = formsOfThisMonth.loc[formsOfThisMonth['is_submitted'] == 1]
            formsOfThisMonth = formsOfThisMonth.loc[formsOfThisMonth['approved_by_level']
                                                    != formsOfThisMonth['max_level_needed']]
            formsOfThisMonth['email'] = "system@redseerconsulting.com"

            # Below lines are for testing and debugging
            # formsOfThisMonth = formsOfThisMonth.loc[formsOfThisMonth['id'] == 2053]
            # formsOfThisMonth = formsOfThisMonth.iloc[:1]
            # print("ApprovalList-", formsOfThisMonth)

            update_statement = "UPDATE reportversion SET approved_by_level = :final_approval_level, email = :email WHERE id = :id"
            insert_statement = "INSERT INTO audit_table (user, user_level, date, action, form_id_id) VALUES (:user, :user_level, :date, :action, :form_id_id)"

            for index, row in formsOfThisMonth.iterrows():
                db_conn.execute(text(update_statement), {
                                "final_approval_level": row['max_level_needed'], "email": row['email'], "id": row['id']})
                for approvalLevel in range(row['approved_by_level']+1, row['max_level_needed']+1):
                    db_conn.execute(text(insert_statement), {
                                    "user": row['email'], "user_level": approvalLevel, "date": todaysDate, "action": 1, "form_id_id": row['id']})
                print(
                    f"Forms autoapprove success! - {row['id']} - {row['company']}!")

            db_conn.commit()
            db_conn.close()
            db_session.close()
            print(
                f"Forms autoapprove success! - {len(formsOfThisMonth)} no of forms have been auto approved!")
        except Exception as e:
            print('Forms autoapprove mets error-', e)
