import uuid
import django
from django.db import models
from .apps import FormapiConfig as AppConfig
# Create your models here.

# sub question. current_value form report result where report version is same by key
class Parameter(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=100)
    question = models.CharField(max_length=255)

    class Meta:
        managed = True
        db_table = str(AppConfig.name) + "_" + "Parameters"


class Company(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField() #is caklled industry

    class Meta:
        managed = True
        db_table = str(AppConfig.name) + "_" + "Company"

# mainquestion. unit = currency. aggretgate = summate
class ParameterTree(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=100)
    question = models.CharField(max_length=255)
    unit = models.CharField(max_length=25)
    parameters = models.ManyToManyField(Parameter)
    summate = models.BooleanField()

    class Meta:
        managed = True
        db_table = str(AppConfig.name) + "_" + "ParameterTree"


#permitted to create different model
class Report(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=100)
    frequency = models.TextField(choices=[(1,"Weekly"),(2,"Monthly"),(3,"Quarterly")])
    cutoff = models.IntegerField()
    companies = models.ManyToManyField(Company)
    parameters = models.ManyToManyField(ParameterTree)

    class Meta:
        managed = True
        db_table = str(AppConfig.name) + "_" + "Report"


# subquestion partner. similar to question  and answermodel you did
class ReportResult(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    # report = models.ForeignKey(ReportVersion, on_delete=models.PROTECT)
    parameter = models.ForeignKey(Parameter, on_delete=models.PROTECT)  # sub question id
    parametertree = models.ForeignKey(ParameterTree, on_delete=models.PROTECT, default='4bd10dec-e812-479a-99bf-4f3deda81fe0')
    value = models.CharField(max_length=100)
    last_updated = models.DateTimeField(default=django.utils.timezone.now)
    source = models.CharField(max_length=20)

    class Meta:
        managed = True
        db_table = str(AppConfig.name) + "_" + "ReportResult"

    # def save(self, *args, **kwargs):
    #     if not self.score:
    #         self.score = self.threat.score
    #     return super().save(*args, **kwargs)


# main model
#
# deadline extra, reportversion. report.paramters count = total questions. no of report result  = filled_count
# last date of report result  = date_mod, schedule, id ,  from report version.
# date_created in report_version =  current_instance.created_at?
# filled_count = no of report result need details as there wil be only one report per report version
# last_modified_date?
# is-submitted?
#


# add a single company field here
# answer =  last value in subquestion fioeld submitted wrt last month
# current_value = value if any submitted in subquestion model
# filled-count = no of subquestions with answers
class ReportVersion(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    name = models.CharField(max_length=100)
    company = models.CharField(max_length=255, default='testCompany')
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    report_result = models.ManyToManyField(ReportResult)
    date_created = models.DateTimeField(default=django.utils.timezone.now)

    class Meta:
        managed = True
        db_table = str(AppConfig.name) + "_" + "ReportVersion"


# remove
class sub_questionsModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    current_value = models.IntegerField()
    last_value = models.IntegerField()
    sub_question = models.CharField(max_length=255)

    class Meta:
        managed = True
        db_table = str(AppConfig.name) + "_" + "sub_questions"

# remove
class questionsModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    aggregate = models.BooleanField(default=True)
    question = models.TextField()
    sub_questions = models.ManyToManyField(sub_questionsModel)

    class Meta:
        managed = True
        db_table = str(AppConfig.name) + "_" + "questions"

# remove?
class insideFormModel(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True)
    company = models.CharField(max_length=255)
    deadline_days = models.IntegerField()
    filled_count = models.IntegerField()
    last_modified_date = models.DateTimeField(null=True, default=django.utils.timezone.now)
    name = models.CharField(max_length=255)
    question_count = models.IntegerField()
    schedule = models.CharField(max_length=255)
    is_submitted = models.BooleanField(default=True)
    current_instance = models.JSONField()
    questions = models.ManyToManyField(questionsModel)

    class Meta:
        managed = True
        db_table = str(AppConfig.name) + "_" + "insideFormModel"
