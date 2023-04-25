from datetime import datetime
from django_apscheduler.jobstores import DjangoJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from RedseerFormAPI.settings import TIME_ZONE
import uuid
from dateutil.relativedelta import relativedelta
import pytz
import calendar
from FormAPI.utils.form_scripts import FormAutomation

createFormsJobId = str(uuid.uuid4())
formAutomationObject = FormAutomation()


def forms_release_job():
    print(f"Forms release job executed at, {TIME_ZONE}-",
          datetime.now(), ", ", createFormsJobId)
    formAutomationObject.forms_auto_release()


approveFormsJobId = str(uuid.uuid4())


def approve_froms_job():
    print(f"Forms autoapprove job started at, {TIME_ZONE}-",
          datetime.now(), ", ", approveFormsJobId)
    formAutomationObject.forms_auto_approve()


delay1FormsJobId = str(uuid.uuid4())


def forms_delay1_notify_job():
    print(f"Forms delay1 notify job started at, {TIME_ZONE}-",
          datetime.now(), ", ", delay1FormsJobId)
    formAutomationObject.forms_delay1_notifications()


delay2FormsJobId = str(uuid.uuid4())


def forms_delay2_notify_job():
    print(f"Forms delay2 notify job started at, {TIME_ZONE}-",
          datetime.now(), ", ", delay2FormsJobId)
    formAutomationObject.forms_delay2_notifications()


testJobId = str(uuid.uuid4())


def test_job():
    print(f"Test job executed, {TIME_ZONE}-", datetime.now(), ", ", testJobId)


def start():
    scheduler = BackgroundScheduler(timezone=TIME_ZONE)
    # scheduler.add_jobstore(DjangoJobStore(), "default")#This is to store the all jobs with there createFormsJobId

    # To run job at midnight of 1st of every month in UTC time, means 05:30 india time
    scheduler.add_job(
        forms_release_job,
        trigger="cron",
        day=1,  # run on the 1st day of every month
        hour=0,
        minute=0,
        id=createFormsJobId
    )

    # To run job at 16:00 IST of last day of every month in UTC time, means 10:30 UTC time
    last_day_of_month = calendar.monthrange(
        datetime.now().year, datetime.now().month)[1]
    scheduler.add_job(
        approve_froms_job,
        trigger=CronTrigger(day=last_day_of_month, month='1-12',
                            hour=10, minute=30, timezone=pytz.utc),  # 16:00 IST
        id=approveFormsJobId
    )

    # To run job at 10:00 IST on 3rd day of every month in UTC time, means 4:30 UTC time
    scheduler.add_job(
        forms_delay1_notify_job,
        trigger="cron",
        day=3,
        hour=4,
        minute=30,
        id=delay1FormsJobId
    )

    # To run job at 10:00 IST every day in UTC time, means 4:30 UTC time
    scheduler.add_job(
        forms_delay2_notify_job,
        trigger="cron",
        hour=4,
        minute=30,
        day="*",  # run every day
        id=delay2FormsJobId
    )

    # for the testing purpose, every 10 second later
    # scheduler.add_job(
    #     test_job,
    #     trigger="cron",
    #     day=21,
    #     hour=14,
    #     minute=29,
    #     id=testJobId
    # )

    # for the testing purpose, every 10 second later
    # scheduler.add_job(
    #     test_job,
    #     trigger="interval",
    #     seconds=15,
    #     id=testJobId
    # )

    scheduler.start()
