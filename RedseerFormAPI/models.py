# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


# class FormapiCompany(models.Model):
#     app_id = models.IntegerField(primary_key=True)
#     app_name = models.CharField(max_length=45, blank=True, null=True)
#     industry_id = models.IntegerField(blank=True, null=True)
#
#     class Meta:
#         managed = False
#         db_table = 'formapi_company'


class FormapiParameters(models.Model):
    parameter_id = models.CharField(primary_key=True, max_length=50)
    parameter_name = models.CharField(max_length=45, blank=True, null=True)
    unit = models.CharField(max_length=20, blank=True, null=True)
    parent_parameter = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'formapi_parameters'


class IndApp(models.Model):
    index = models.IntegerField(primary_key=True)
    industry_name = models.CharField(max_length=45, blank=True, null=True)
    app_name = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ind_app'


class Industry(models.Model):
    industry_id = models.IntegerField(primary_key=True)
    industry_name = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'industry'


class InternetIndustries(models.Model):
    index = models.BigIntegerField(blank=True, null=True)
    industry_id = models.BigIntegerField(blank=True, null=True)
    app_id = models.BigIntegerField(blank=True, null=True)
    market_share = models.BigIntegerField(blank=True, null=True)
    net_revenue = models.BigIntegerField(blank=True, null=True)
    no_of_subscribers = models.BigIntegerField(blank=True, null=True)
    avg_dau = models.BigIntegerField(blank=True, null=True)
    mau = models.BigIntegerField(blank=True, null=True)
    ad_revenue = models.BigIntegerField(blank=True, null=True)
    market_share_percentage = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'internet_industries'


class MainData(models.Model):
    player = models.ForeignKey('Player', models.DO_NOTHING, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    parameter = models.ForeignKey('Parameter', models.DO_NOTHING, blank=True, null=True)
    value = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    date_created = models.DateField(blank=True, null=True)
    source = models.CharField(max_length=45, blank=True, null=True)
    report_version = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'main_data'


class Parameter(models.Model):
    parameter_id = models.AutoField(primary_key=True)
    parameter_name = models.CharField(max_length=80, blank=True, null=True)
    unit = models.CharField(max_length=20, blank=True, null=True)
    parent_parameter = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'parameter'


class Player(models.Model):
    player_id = models.IntegerField(primary_key=True)
    player_name = models.CharField(max_length=45, blank=True, null=True)
    industry_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'player'
