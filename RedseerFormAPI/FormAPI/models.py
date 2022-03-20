import uuid
import django
from django.db import models
import calendar
import datetime
from datetime import date
from .apps import FormapiConfig as AppConfig
# Create your models here.

# sub question. current_value form report result where report version is same by key
# remove many to many from parameter tree and add  parent_parameter as foriegn key
# parent_parameter-NAME


class FormapiParameter(models.Model):
    parameter_id = models.AutoField(primary_key=True)
    parameter_name = models.CharField(max_length=80, blank=True, null=True)
    unit = models.CharField(max_length=20, blank=True, null=True)
    parent_parameter = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'formapi_parameter'



# previously called company
class Player(models.Model):
    player_id = models.AutoField(primary_key=True, auto_created=True)
    player_name = models.CharField(max_length=45)
    industry_id = models.IntegerField(default=3) #is caklled industry

    class Meta:
        managed = False
        db_table = "player"


class Parameter(models.Model):
    parameter_id = models.AutoField(primary_key=True)
    parameter_name = models.CharField(max_length=80, blank=True, null=True)
    unit = models.CharField(max_length=20, blank=True, null=True)
    parent_parameter = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'parameter'


# mainquestion. unit = currency. aggretgate = summate
class ParameterTree(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    question = models.CharField(max_length=255)
    # unit = models.CharField(max_length=25)
    parameters = models.ManyToManyField(Parameter)
    summate = models.BooleanField(default = True)

    class Meta:
        managed = False


# permitted to create different model
class Report(models.Model):
    id = models.AutoField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=100)
    frequency = models.TextField(choices=[(1,"Weekly"),(2,"Monthly"),(3,"Quarterly")])
    cutoff = models.IntegerField(default=15)
    companies = models.ManyToManyField(Player)
    question = models.ManyToManyField(ParameterTree)

    class Meta:
        managed = False
        db_table = "report"
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
    company = models.CharField(max_length=255, default='testCompany')
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    date_created = models.DateTimeField(default=django.utils.timezone.now)

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
    date_created = models.DateField(blank=True, null=True)
    source = models.CharField(max_length=45, blank=True, null=True)
    parametertree = models.ForeignKey(ParameterTree, on_delete=models.PROTECT, default=1)
    report_version = models.ForeignKey(ReportVersion, on_delete=models.PROTECT, default=1)

    class Meta:
        managed = False
        db_table = 'main_data'



#
#
# # remove
# class sub_questionsModel(models.Model):
#     id = models.UUIDField(default=uuid.uuid4, primary_key=True)
#     current_value = models.IntegerField()
#     last_value = models.IntegerField()
#     sub_question = models.CharField(max_length=255)
#
#     class Meta:
#         managed = True
#         db_table = str(AppConfig.name) + "_" + "sub_questions"
#
# # remove
# class questionsModel(models.Model):
#     id = models.UUIDField(default=uuid.uuid4, primary_key=True)
#     aggregate = models.BooleanField(default=True)
#     question = models.TextField()
#     sub_questions = models.ManyToManyField(sub_questionsModel)
#
#     class Meta:
#         managed = True
#         db_table = str(AppConfig.name) + "_" + "questions"
#
# # remove?
# class insideFormModel(models.Model):
#     id = models.UUIDField(default=uuid.uuid4, primary_key=True)
#     company = models.CharField(max_length=255)
#     deadline_days = models.IntegerField()
#     filled_count = models.IntegerField()
#     last_modified_date = models.DateTimeField(null=True, default=django.utils.timezone.now)
#     name = models.CharField(max_length=255)
#     question_count = models.IntegerField()
#     schedule = models.CharField(max_length=255)
#     is_submitted = models.BooleanField(default=True)
#     current_instance = models.JSONField()
#     questions = models.ManyToManyField(questionsModel)
#
#     class Meta:
#         managed = True
#         db_table = str(AppConfig.name) + "_" + "insideFormModel"
