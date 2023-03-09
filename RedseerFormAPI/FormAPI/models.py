import uuid
import django
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.core.mail import EmailMessage
from django.conf import settings
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import date, timedelta
from .service_utils import CalculatedParamFn
from .service_utils_foodtech import CalculatedParamFoodtechFn
import calendar
import datetime
import requests
import json
from datetime import date
from dotenv import load_dotenv
import os
from .apps import FormapiConfig as AppConfig
# Create your models here.

# sub question. current_value form report result where report version is same by key
# remove many to many from parameter tree and add  parent_parameter as foriegn key
# parent_parameter-NAME

cred = credentials.Certificate('/Users/shahzmaalif/Documents/GitHub/RedseerAPI/RedseerFormAPI/coeus-8be26-firebase-adminsdk-panol-ec5a6f11fd.json')
firebase_admin.initialize_app(cred)
db = firestore.client()
load_dotenv()

#ignore it
# class FormapiParameter(models.Model):#old model, not in use
#     parameter_id = models.AutoField(primary_key=True)
#     parameter_name = models.CharField(max_length=80, blank=True, null=True)
#     unit = models.CharField(max_length=20, blank=True, null=True)
#     parent_parameter = models.CharField(max_length=45, blank=True, null=True)

#     class Meta:
#         managed = False
#         db_table = 'formapi_parameter'

class Sector(models.Model):
    sector_id = models.AutoField(primary_key=True, auto_created=True)
    sector_name = models.CharField(max_length=45)
    class Meta:
        managed = False
        db_table = "sector"

    def __str__(self): #'sector_name' is being used as attribute to identify Report objects 
        return self.sector_name
    
class Industry(models.Model):
    industry_id = models.AutoField(primary_key=True, auto_created=True)
    industry_name = models.CharField(max_length=45)
    sector = models.ForeignKey(Sector, models.DO_NOTHING, blank=True, null=True)
    order = models.IntegerField(default=0)
    sector_name = models.CharField(max_length=45)
    class Meta:
        managed = False
        db_table = "industry"
    
    def __str__(self): #'industry_name' is being used as attribute to identify Report objects 
        return self.industry_name

# previously called company
class Player(models.Model):
    player_id = models.AutoField(primary_key=True, auto_created=True)
    player_name = models.CharField(max_length=45)
    industry = models.ForeignKey(Industry, models.DO_NOTHING, blank=True, null=True) #is called industry
    excel_link = models.CharField(max_length=2000)
    last_date_day = models.IntegerField(default=28, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "player"
    
    def __str__(self): #'player_name' is being used as attribute to identify Report objects 
        return self.player_name


class Parameter(models.Model):
    parameter_id = models.AutoField(primary_key=True)
    parameter_name = models.CharField(max_length=80, blank=True, null=True)
    unit = models.CharField(max_length=20, blank=True, null=True)
    parent_parameter = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'parameter'
    
    def __str__(self): #'parameter_name' is being used as attribute to identify Report objects 
        return self.parameter_name  or '----- ERROR: NULL VALUE FOUND ----'


# mainquestion. unit = currency. aggregate = summate
class ParameterTree(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    question = models.CharField(max_length=255)
    # unit = models.CharField(max_length=25)
    parameters = models.ManyToManyField(Parameter)
    summate = models.BooleanField(default = True)

    class Meta:
        managed = False

    def __str__(self): #'question' is being used as attribute to identify Report objects 
        return self.question or '----- ERROR: NULL VALUE FOUND ----'


# permitted to create different model
class Report(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=100)
    frequency = models.TextField(choices=[("1","Weekly"),("2","Monthly"),("3","Quarterly")])
    cutoff = models.IntegerField(default=15) # change default to 30
    question_count = models.IntegerField(default=24)
    companies = models.ManyToManyField(Player)
    question = models.ManyToManyField(ParameterTree)
    max_level_needed = models.IntegerField(default=3)
    form_relase_date = models.IntegerField(default=1, validators=[MaxValueValidator(31),
                                                                   MinValueValidator(1)])
    form_active_days = models.IntegerField(default=15, validators=[MaxValueValidator(100),
                                                                   MinValueValidator(1)])

    class Meta:
        managed = False
        db_table = "report"
    
    def __str__(self): #'name' is being used as attribute to identify Report objects 
        return self.name
#
#
# # main model
# #
# # deadline extra, reportversion. report.paramters count = total questions. no of report result  = filled_count
# # last date of report result  = date_mod, schedule, id ,  from report version.
# # date_created in report_version =  current_instance.created_at?
# # filled_count = no of report result need details as there wil be only one report per report version
# # last_modified_date?
# # is-submitted?
# #
#
#
# # add a single company field here
# # answer =  last value in subquestion fioeld submitted wrt last month
# # current_value = value if any submitted in subquestion model
# # filled-count = no of subquestions with answers
class ReportVersion(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=255, default='testCompany') # this should be a foriegn key
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    filled_count = models.IntegerField(default=0)
    is_submitted = models.BooleanField(default=False)
    status = models.IntegerField(default=0)
    email = models.CharField(max_length=1000, default=None)
    approved_by_level = models.IntegerField(default=1)
    max_level_needed = models.IntegerField(default=5)
    date_created = models.DateTimeField(default=django.utils.timezone.now)
    closing_time = models.DateTimeField(blank = True)

    def __str__(self):
        return str(self.id) + " - " + self.name

    class Meta:
        managed = False
        db_table = "reportversion"
#
# # subquestion partner. similar to question  and answermodel you did
# # add report version name, parameter name,startdate, enddate ,  deafult source = benchmarkteam ,
# # comapny = reportversion company
# # class ReportResult(models.Model):
# #     # id = models.UUIDField(default=uuid.uuid4, primary_key=True)
# #     report = models.ForeignKey(ReportVersion, on_delete=models.PROTECT, default=1)
# #     parameter = models.ForeignKey(Parameter, on_delete=models.PROTECT)  # sub question id
# #     parametertree = models.ForeignKey(ParameterTree, on_delete=models.PROTECT, default='4bd10dec-e812-479a-99bf-4f3deda81fe0')
# #     value = models.CharField(max_length=100)
# #     last_updated = models.DateTimeField(default=django.utils.timezone.now) # make it date_created
# #     source = models.CharField(max_length=20, default='benchmarkteam')
# #     start_date = models.DateField(default=datetime.date.today().replace(day=1))
# #     end_date = models.DateField(default=date.today().replace(day=calendar.monthrange(date.today().year, date.today().month)[1]))
# #     # company_id = models.ForeignKey(Company , on_delete=models.PROTECT)
# #     # parameter_name = models.TextField()
# #     report_version_name = models.TextField(default='default_report_version_name')
# #
# #     class Meta:
# #         managed = True
# #         db_table = str(AppConfig.name) + "_" + "ReportResult"
#
#
# class MainData(models.Model):
#     id = models.AutoField(auto_created=True, primary_key=True)
#     player_id = models.ForeignKey(Player, on_delete=models.PROTECT)
#     start_date = models.DateField(default=datetime.date.today().replace(day=1))
#     end_date = models.DateField(
#         default=date.today().replace(day=calendar.monthrange(date.today().year, date.today().month)[1]))
#     parameter_id = models.ForeignKey(Parameter, on_delete=models.PROTECT) # sub question id
#     value = models.FloatField()
#     date_created = models.DateField(default=datetime.date.today())
#     source = models.CharField(max_length=45, default='benchmark_team')
#     report_version = models.CharField(max_length=45, default='Report_Version_Name')
#     # where we getting there
#     report_version_id = models.ForeignKey(ReportVersion, on_delete=models.PROTECT, default=1)
#     parametertree = models.ForeignKey(ParameterTree, on_delete=models.PROTECT, default='4bd10dec-e812-479a-99bf-4f3deda81fe0')
#
#     class Meta:
#         managed = True
#         db_table = "main_data"


#reportresult
class MainData(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    player = models.ForeignKey('Player', models.DO_NOTHING, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    parameter = models.ForeignKey('Parameter', models.DO_NOTHING, blank=True, null=True)
    value = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    remark = models.CharField(max_length=200, blank=True, null=True)
    date_created = models.DateField(blank=True, null=True)
    source = models.CharField(max_length=45, blank=True, null=True)
    parametertree = models.ForeignKey(ParameterTree, on_delete=models.PROTECT, default=1)
    report_version = models.ForeignKey(ReportVersion, on_delete=models.PROTECT, default=1)

    class Meta:
        managed = False
        db_table = 'main_data'


class AuditTable(models.Model):
    user = models.CharField(max_length=1000, default=None)  #email
    user_level = models.IntegerField(default=1)
    date = models.DateTimeField(auto_now_add=True, blank=True)
    action = models.BooleanField(default=False)
    form_id = models.ForeignKey(ReportVersion, on_delete=models.PROTECT, default=1)

    class Meta:
        managed = True
        db_table = 'audit_table'


class MainDataProd(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    player = models.ForeignKey('Player', models.DO_NOTHING, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    parameter = models.ForeignKey('Parameter', models.DO_NOTHING, blank=True, null=True)
    value = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    remark = models.CharField(max_length=200, blank=True, null=True)
    date_created = models.DateField(blank=True, null=True)
    source = models.CharField(max_length=45, blank=True, null=True)
    parametertree = models.ForeignKey(ParameterTree, on_delete=models.PROTECT, default=1)
    report_version = models.ForeignKey(ReportVersion, on_delete=models.PROTECT, default=1)

    class Meta:
        managed = False
        db_table = 'main_data_prod'

# Table relations
class ReportQuestion(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    report = models.ForeignKey(Report, on_delete=models.PROTECT)
    parametertree = models.ForeignKey(ParameterTree, on_delete=models.PROTECT)
    sequence = models.IntegerField(default=0, null=False)

    class Meta:
        managed = False
        db_table = 'report_question'

class ReportCompanies(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    report = models.ForeignKey(Report, on_delete=models.PROTECT, blank=True, null=True)
    player = models.ForeignKey(Player, on_delete=models.PROTECT, blank=True, null=True) #is called industry

    class Meta:
        managed = False
        db_table = "report_companies"
    
    def __str__(self): #'player_name' is being used as attribute to identify Report objects 
        return self.report + " - " + self.player


@receiver(pre_save, sender=ReportVersion)
def notify_denial_by_email(sender, instance, **kwargs):
    # previous here refers to current instance of row in reportversion table
    try:
        previous = ReportVersion.objects.filter(id=instance.id)
        print('email will be sent to notify if denial by email')
        # below condition works bea=cause no email exists for 1st submission
        # previous[0 wont work if there is no previous instance hence not work for forms which are new. Also issues with others
        if previous[0].is_submitted != instance.is_submitted:
            print('check submit condition')
            if previous[0].email:
                print(previous[0].email)
                msg = EmailMessage(
                    'WebForm Denied',
                    f'Welcome Back , <br><br> Your Webform【{previous[0].name}】was denied',
                    settings.EMAIL_HOST_USER,
                    [previous[0].email]
                )
                msg.content_subtype = "html"
                mail_status = msg.send()
            else:
                print('no email present')
    except:
        pass


@receiver(pre_save, sender=ReportVersion)
def notify_approval_by_email(sender, instance,**kwargs):
    try:
        previous = ReportVersion.objects.filter(id=instance.id)
        if previous[0].approved_by_level + 1 == instance.approved_by_level:
            user_ref = db.collection(u'users')
            docs = user_ref.stream()
            user_list = []
            email_list = []
            for doc in docs:
                user_list.append(doc.to_dict())
            for i in user_list:
                assigned_rep = i.get('assigned_reports')
                if assigned_rep:
                    for j in assigned_rep:
                        if j.get('level') == str(instance.approved_by_level+1) and j.get('report_id') == instance.report_id:
                            email_list.append(i.get('email'))
            if email_list:
                msg = EmailMessage(
                    'WebForm Available',
                    f'Welcome Back , <br><br> New Webform【{instance.name}】is available for approval',
                    settings.EMAIL_HOST_USER,
                    email_list
                )
                msg.content_subtype = "html"
                mail_status = msg.send()
            else:
                print('no email present')
    except:
        pass


@receiver(post_save, sender=ReportVersion)
def fill_main_data_prod(sender, instance, created, **kwargs):
    max_level = Report.objects.filter(id=instance.report_id)[0].max_level_needed
    if instance.approved_by_level == max_level:
        qs_main_data = MainData.objects.filter(report_version=instance.id)
        for i in qs_main_data:
            i_dict = i.__dict__
            i_dict.pop('id')  # remove primary key from dict
            i_dict.pop('_state')
            MainDataProd.objects.create(**i_dict)


# fill audit table when user 1st fills data. user data from patching is done directly by website.approved_by_level
# should be 1 by default. We are not recoridng approved by level when 1st submit.need to disable when creating webform
@receiver(post_save, sender=ReportVersion)
def fill_audit_table(sender, instance, created, **kwargs):
    try:
        if instance.approved_by_level == 1 and instance.date_created.date() != datetime.date.today():
            user_level = 1
            user =instance.email
            action = True
            form_id = ReportVersion.objects.filter(id=instance.id)[0]
            AuditTable.objects.create(user=user, user_level=user_level, action=action, form_id = form_id)
    except:
        pass


@receiver(post_save, sender=ReportVersion)
def refresh_power_bi(sender, instance, created, **kwargs):
    print('refresh fn triggered')
        # refresh power bi. should run 1 time only so need to make changes to if condition
    try:
        if instance.is_submitted and instance.approved_by_level == 1:
            date_created = instance.date_created
            end_date = date_created.replace(day=1) - timedelta(days=1)
            start_date = date_created.replace(day=1) - timedelta(days=end_date.day)
            start_date = str(start_date.date())
            end_date = str(end_date.date())
            report_id = instance.report_id
            player_id = Player.objects.filter(player_name=instance.company)[0].player_id
            try:
                tmp = CalculatedParamFn()
                tmpFoodtech = CalculatedParamFoodtechFn() 
                if report_id == 14:
                    tmpFoodtech.report_version_id(instance.id)
                if report_id == 45:
                    tmp.calc_script_eb2b(player_id, start_date, end_date)
                if report_id == 46:
                    tmp.calc_script_eb2bGrocery(player_id, start_date, end_date)
                if report_id == 47:
                    tmp.calc_script_eb2bElectronics(player_id, start_date, end_date)
                if report_id == 48:
                    tmp.calc_script_eb2bEPharma(player_id, start_date, end_date)
                if report_id == 6:
                    tmp.calc_script_csm(player_id, start_date, end_date)
                if report_id == 5:
                    tmp.calc_script_shortform(player_id, start_date, end_date)
                if report_id == 1:
                    tmp.calc_script_video(player_id, start_date, end_date)
                if report_id == 4:
                    tmp.calc_script_audio(player_id, start_date, end_date)
                if report_id == 33:
                    tmp.calc_script_rmg(player_id, start_date, end_date)
                if report_id == 36:
                    tmp.calc_script_usedCars(player_id, start_date, end_date)
                if report_id == 40:
                    tmp.calc_script_meatCore(player_id, start_date, end_date)
                if report_id == 41:
                    tmp.calc_script_meatMarketPlace(player_id, start_date, end_date)
                if report_id == 42:
                    tmp.calc_script_d2c(player_id, start_date, end_date)
                if report_id == 28:
                    tmp.calc_script_edtech(player_id, start_date, end_date)
                if report_id == 43:
                    tmp.calc_script_mobility(player_id, start_date, end_date)
                if report_id == 19:
                    tmp.calc_script_horizontals(player_id, start_date, end_date)
                if report_id == 54:
                    tmp.calc_script_foodtech(player_id, start_date, end_date)
                if report_id == 25:
                    tmp.calc_script_ehealth(player_id, start_date, end_date)
            except:
                pass

        workspace_id = os.getenv("workspace_id")
        url = "https://login.microsoftonline.com/common/oauth2/token"
        data = {"grant_type": "password",
                "username": os.getenv('username'),
                "password": os.getenv('password'),
                "client_id": os.getenv('client_id'),
                "client_secret": os.getenv('client_secret'),
                "resource": "https://analysis.windows.net/powerbi/api"}

        login_output = requests.post(url, data=data)
        login_output = login_output.json()
        access_token = login_output["access_token"]
        auth_url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/reports/"
        auth_output = requests.get(auth_url, headers={'Authorization': f'Bearer {access_token}'})

        report_list = auth_output.json()["value"]

        required_name_list = ['Sectors_Company_Profile']
        for report in report_list:
            if report["name"] in required_name_list:
                dataset_id = report["datasetId"]
                refresh_url = f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset_id}/refreshes"
                response = requests.post(refresh_url, headers={'Authorization': f'Bearer {access_token}'})
                print(report["name"], response)
    except:
        pass
