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
from django.core.mail import EmailMessage
from firebase_admin import firestore
from ..api_views import ReportVersionCView
import smtplib
# from threading import Semaphore


db_settings = settings.DATABASES['default']
firebase_db = firestore.client()


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

    def forms_pre_release_notify(self):
        db = pymysql.connect(
            host=db_settings['HOST'],
            port=int(db_settings['PORT']),
            user=db_settings['USER'],
            password=db_settings['PASSWORD'],
            db=db_settings['NAME'],
            ssl={'ssl': {'tls': True}}
        )
        db_cur = db.cursor()

        db_cur.execute("select player_name, report.id, report.name from((industry INNER JOIN report ON industry.industry_name = report.name) INNER JOIN player ON industry.industry_id = player.industry_id and player.is_active = 1);")
        playersTuples = db_cur.fetchall()
        db_cur.close()

        forms_table_data = []
        sNo = 1
        for player_name, id, name in playersTuples:
            forms_table_data.append(
                {"sNo": sNo, "webformName": player_name+' Input', "playerName": player_name, "industryName": name})
            sNo = sNo+1

        admin_email_list = []
        user_ref = firebase_db.collection(u'users')
        docs = user_ref.stream()
        user_list = []
        for doc in docs:
            user_list.append(doc.to_dict())
        for i in user_list:
            if (i.get('is_admin')):
                admin_email_list.append(i.get('email'))

        try:
            if admin_email_list and forms_table_data:
                print(
                    f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Log: Fors pre release notify script triggered. Sending emails to admin teams')
                try:
                    shared_style = "border: 1px solid #dddddd; text-align: left; padding: 8px;"
                    table_style = "font-family: arial, sans-serif;"
                    table_headings = """
                        <tr>
                            <td style="{}">S.No.</td>
                            <td style="{}">Webform Name</td>
                            <td style="{}">Player Name</td>
                            <td style="{}">Industry Name</td>
                        </tr>
                    """.format(
                        shared_style,
                        shared_style,
                        shared_style,
                        shared_style,
                    )

                    table_rows = ""
                    for data in forms_table_data:
                        table_rows += """
                            <tr>
                                <td style="{}">{}</td>
                                <td style="{}">{}</td>
                                <td style="{}">{}</td>
                                <td style="{}">{}</td>
                            </tr>
                        """.format(
                            shared_style, data["sNo"],
                            shared_style, data["webformName"],
                            shared_style, data["playerName"],
                            shared_style, data["industryName"],
                        )

                    html_content = """
                        <h2 style="{}">Preview of Next Month's Webforms Release: See What's in List!</h2>
                        <p>
                            Here is a list of webforms scheduled to be released on the 1st of next month. Kindly review the list and bring to the attention of the Development Team if there are any missing or extra webforms.
                        </p>
                        <table style="{} border-collapse: collapse; width: 100%;">
                            {}
                            {}
                        </table>
                    """.format(table_style, table_style, table_headings, table_rows)

                    msg = EmailMessage(
                        'WebForms Pre-Release Review Notification',
                        html_content,
                        settings.EMAIL_HOST_USER,
                        admin_email_list
                    )
                    msg.content_subtype = "html"

                    mail_status = msg.send()
                    if (mail_status == 1):
                        print(
                            f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Log: Form forms_pre_release_notify script completed. Notification successfully sent to {admin_email_list}')
                    else:
                        print(
                            f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Log: Form forms_pre_release_notify script completed, but it seems email notification failed')
                except Exception as e:
                    print(
                        f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Error: Forms forms_pre_release_notify script mets error-', e)
        except:
            print(
                f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Error: Forms forms_pre_release_notify error -', e)

    def forms_auto_release(self):
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

        cur.execute("select id, name from report;")
        industriesTuples = cur.fetchall()
        cur.close()
        industryNames = {}
        for id, name in industriesTuples:
            industryNames[id] = name
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
        all_email_list = []
        user_ref = firebase_db.collection(u'users')
        docs = user_ref.stream()
        user_list = []
        for doc in docs:
            user_list.append(doc.to_dict())
        for i in user_list:
            all_email_list.append(i.get('email'))

        print(
            f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Log: new form will be created for -', industryWiseData)
        url = "/formresult/1/1/"
        factory = APIRequestFactory()
        forms_table_data = []
        sNo = 1
        try:
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
                        request = factory.post(
                            url, request_data, format='json')
                        # response = requests.request(
                        #     "POST", url, headers=headers, data=payload)
                        view = ReportVersionCView.as_view()
                        response = view(request)
                        if response.status_code == 200:
                            forms_table_data.append(
                                {"sNo": sNo, "webformName": j+' Input', "playerName": j, "industryName": industryNames[i]})
                            sNo = sNo+1
                            if 'text/html' in response.headers['content-type']:
                                # if response.content_type == 'application/json':
                                response.render()
                                content = json.loads(response.content)
                                print(
                                    f"{datetime.now().strftime('[%d/%b/%Y %H:%M:%S]')} Log: Form Create success id={content['current_instance']['id']}, player={j}, created_at={content['current_instance']['created_at']}")
                            else:
                                print(
                                    f"{datetime.now().strftime('[%d/%b/%Y %H:%M:%S]')} Log: Form Create success id={content['current_instance']['id']}, player={j}, created_at={content['current_instance']['created_at']}, some error might be expected")
                        else:
                            print(
                                f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Error: Form Create error, player={j} and report_id={i}')
                    except Exception as e:
                        print(
                            f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Error: Form auto release error, player={j} and report_id={i}', e)
        except:
            print(
                f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Error: Form auto release error -', e)
        finally:
            if all_email_list and forms_table_data:
                print(
                    f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Log: Form auto release script has been completed. Sending emails to relevant teams')
                try:
                    shared_style = "border: 1px solid #dddddd; text-align: left; padding: 8px;"
                    table_style = "font-family: arial, sans-serif;"
                    table_headings = """
                        <tr>
                            <td style="{}">S.No.</td>
                            <td style="{}">Webform Name</td>
                            <td style="{}">Player Name</td>
                            <td style="{}">Industry Name</td>
                        </tr>
                    """.format(
                        shared_style,
                        shared_style,
                        shared_style,
                        shared_style,
                    )

                    table_rows = ""
                    for data in forms_table_data:
                        table_rows += """
                            <tr>
                                <td style="{}">{}</td>
                                <td style="{}">{}</td>
                                <td style="{}">{}</td>
                                <td style="{}">{}</td>
                            </tr>
                        """.format(
                            shared_style, data["sNo"],
                            shared_style, data["webformName"],
                            shared_style, data["playerName"],
                            shared_style, data["industryName"],
                        )

                    html_content = """
                        <h2 style="{}">Webforms for this month have been released</h2>
                        <p>
                            Kindly fill out your assigned webforms as soon as possible. <br/>Your webform
                            will be auto-saved even if you can't submit it.
                        </p>
                        <table style="{} border-collapse: collapse; width: 100%;">
                            {}
                            {}
                        </table>
                    """.format(table_style, table_style, table_headings, table_rows)

                    msg = EmailMessage(
                        'New WebForms Released',
                        html_content,
                        settings.EMAIL_HOST_USER,
                        all_email_list
                    )
                    msg.content_subtype = "html"

                    mail_status2 = msg.send()
                    if (mail_status2 == 1):
                        print(
                            f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Log: Form forms_auto_release completed. Notification successfully sent to {all_email_list}')
                    else:
                        print(
                            f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Log: Form forms_auto_release completed, but it seems email notification failed')
                except Exception as e:
                    print(
                        f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Error: Forms forms_auto_release mets error-', e)

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

    def forms_delay1_notifications(self):
        # This will get triggered on 3rd of every month
        todaysDateDay = int(datetime.now().day)  # equals to 3 for now
        next4DateDay = todaysDateDay + 4
        monthStartDate = datetime.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0)

        try:
            db_session, db_conn = self.get_db_connection()
            # last_date_day > {next4DateDay} in below line is because, delay1 will only get sent
            delayedFormsOfThisMonth = pd.read_sql(text(
                f"SELECT id, name, report_id, approved_by_level, is_submitted, player.last_date_day FROM reportversion INNER JOIN player ON reportversion.company = player.player_name WHERE date_created >= '{monthStartDate}' and is_submitted = 0 and last_date_day > {next4DateDay};"), db_conn)
            print(
                f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Log: Form delay1 report, {len(delayedFormsOfThisMonth)} no. of forms are getting delayed!')

            user_ref = firebase_db.collection(u'users')
            docs = user_ref.stream()
            user_list = []
            for doc in docs:
                user_list.append(doc.to_dict())

            levelWiseReportEmails = {}
            for i in user_list:
                assigned_rep = i.get('assigned_reports')
                email = i.get('email')
                if assigned_rep:
                    for j in assigned_rep:
                        report_id = str(j.get('report_id'))
                        level = str(j.get('level'))
                        if report_id in levelWiseReportEmails:
                            if level in levelWiseReportEmails[report_id]:
                                levelWiseReportEmails[report_id][level].append(
                                    email)
                            else:
                                levelWiseReportEmails[report_id][level] = [
                                ] + [email]
                        else:
                            levelWiseReportEmails[report_id] = {}
                            levelWiseReportEmails[report_id][level] = [
                            ] + [email]

            for index, row in delayedFormsOfThisMonth.iterrows():
                form_id = row['id']
                formName = row['name']
                last_date_day = row['last_date_day']
                delayedDays = todaysDateDay - last_date_day
                print(
                    f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Log: Form {form_id} has been delayed, sending delay1 notification...')

                email_list = []
                report_id = str(row['report_id'])
                delayed_level = str(int(row['approved_by_level']) + 1)
                if report_id in levelWiseReportEmails and delayed_level in levelWiseReportEmails[report_id]:
                    email_list = levelWiseReportEmails[report_id][delayed_level]
                if email_list:
                    try:
                        msg = EmailMessage(
                            'WebForm is Pending',
                            f'Dear user,<br><br>Your webform <b><i>{formName}</i></b> has been pending for 2 days, and the final approval deadline is on the {last_date_day} of this month. We kindly request that you fill it out as soon as possible to ensure a smoother process.',
                            settings.EMAIL_HOST_USER,
                            email_list
                        )
                        msg.content_subtype = "html"
                        mail_status = msg.send()
                        if (mail_status == 1):
                            print(
                                f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Log: Form {form_id} delay1 notification sent to {email_list}')
                    except Exception as e:
                        print(
                            f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Error: Form {form_id} delay1 notification error -', e)
                else:
                    print(
                        f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Error: Form {form_id} delay1 notification issue - No email present!')

        except Exception as e:
            print(
                f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Error: forms_delay1_notifications mets error-', e)

    def forms_delay2_notifications(self):
        todaysDateDay = int(datetime.now().day)
        next4DateDay = todaysDateDay + 4
        monthStartDate = datetime.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0)

        try:
            db_session, db_conn = self.get_db_connection()
            delayedFormsOfThisMonth = pd.read_sql(text(
                f"SELECT id, name, report_id, approved_by_level, is_submitted, player.last_date_day FROM reportversion INNER JOIN player ON reportversion.company = player.player_name WHERE date_created >= '{monthStartDate}' and is_submitted = 0 and last_date_day = {next4DateDay};"), db_conn)
            print(
                f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Log: Form delay2 report, {len(delayedFormsOfThisMonth)} no. of forms are getting delayed!')

            user_ref = firebase_db.collection(u'users')
            docs = user_ref.stream()
            user_list = []
            for doc in docs:
                user_list.append(doc.to_dict())

            levelWiseReportEmails = {}
            for i in user_list:
                assigned_rep = i.get('assigned_reports')
                email = i.get('email')
                if assigned_rep:
                    for j in assigned_rep:
                        report_id = str(j.get('report_id'))
                        level = str(j.get('level'))
                        if report_id in levelWiseReportEmails:
                            if level in levelWiseReportEmails[report_id]:
                                levelWiseReportEmails[report_id][level].append(
                                    email)
                            else:
                                levelWiseReportEmails[report_id][level] = [
                                ] + [email]
                        else:
                            levelWiseReportEmails[report_id] = {}
                            levelWiseReportEmails[report_id][level] = [
                            ] + [email]

            for index, row in delayedFormsOfThisMonth.iterrows():
                form_id = row['id']
                formName = row['name']
                delayedDays = todaysDateDay - row['last_date_day']
                print(
                    f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Log: Form {form_id} has been delayed, sending delay2 notification...')

                email_list = []
                report_id = str(row['report_id'])
                delayed_level = str(int(row['approved_by_level']) + 1)
                if report_id in levelWiseReportEmails and delayed_level in levelWiseReportEmails[report_id]:
                    email_list = levelWiseReportEmails[report_id][delayed_level]
                if email_list:
                    try:
                        msg = EmailMessage(
                            'WebForm Getting Delayed',
                            f'Dear user,<br><br>This is to inform you that your webform <b><i>{formName}</i></b> is getting delayed due to incomplete information from your end. As the deadline for final approval is in 4 days, you are requested to fill the same at the earliest to avoid further delay.',
                            settings.EMAIL_HOST_USER,
                            email_list
                        )
                        msg.content_subtype = "html"
                        mail_status = msg.send()
                        if (mail_status == 1):
                            print(
                                f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Log: Form {form_id} delay2 notification sent to {email_list}')
                    except Exception as e:
                        print(
                            f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Error: Form {form_id} delay2 notification error -', e)
                else:
                    print(
                        f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Error: Form {form_id} delay2 notification issue - No email present!')

        except Exception as e:
            print(
                f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")} Error: forms_delay2_notifications mets error-', e)
