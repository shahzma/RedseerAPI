from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Sector, Industry, Player, Parameter, ParameterTree, Report, ReportVersion, MainData, AuditTable, MainDataProd, ReportQuestion, ReportCompanies


class SectorAdmin(admin.ModelAdmin):
    list_display = ('sector_id', 'sector_name')
    ordering = ('sector_id',)
    search_fields = ['sector_name']


class IndustryAdmin(admin.ModelAdmin):
    list_display = ('industry_id', 'industry_name', 'sector', 'sector_name')
    ordering = ('industry_id',)
    search_fields = ['industry_id', 'industry_name',
                     'sector__sector_name', 'sector_name']


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('player_id', 'player_name', 'industry', 'last_date_day', 'is_active')
    ordering = ('player_id',)
    search_fields = ['player_id', 'player_name',
                     'industry__industry_name', 'last_date_day']


class ParameterAdmin(admin.ModelAdmin):
    list_display = ('parameter_id', 'parameter_name')
    ordering = ('parameter_id',)
    search_fields = ['parameter_id', 'parameter_name']


class ParameterTreeAdmin(admin.ModelAdmin):
    list_display = ('id', 'question')
    ordering = ('id',)
    search_fields = ['id', 'question']


class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'industry', 'max_level_needed',
                    'form_relase_date', 'form_active_days')
    ordering = ('id',)
    search_fields = ['id', 'name', 'industry__industry_id']


class ReportVersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company', 'report',
                    'date_created', 'closing_time', 'is_submitted')
    ordering = ('id',)
    search_fields = ['id', 'name', 'company', 'report__name',
                     'date_created', 'closing_time']


class MainDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'player', 'start_date',
                    'parametertree', 'report_version')
    ordering = ('-start_date',)
    search_fields = ['start_date', 'player__player_name',
                     'parametertree__question', 'report_version__id', 'report_version__name']


class AuditTableAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_level', 'form_id')
    ordering = ('user_level',)
    search_fields = ['user', 'form_id__name', 'form_id__id']


class MainDataProdAdmin(admin.ModelAdmin):
    list_display = ('id', 'player', 'start_date',
                    'parametertree', 'report_version')
    ordering = ('-start_date',)
    search_fields = ['start_date', 'player__player_name',
                     'parametertree__question', 'report_version__id', 'report_version__name']


class ReportQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'report', 'parametertree', 'sequence')
    ordering = ('id',)
    search_fields = ['report__name', 'parametertree__question']


class ReportCompaniesAdmin(admin.ModelAdmin):
    list_display = ('id', 'report', 'player')
    ordering = ('id',)
    search_fields = ['report__name', 'player__player_name']


# Register your models here.
admin.site.register(Sector, SectorAdmin)
admin.site.register(Industry, IndustryAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(Parameter, ParameterAdmin)
admin.site.register(ParameterTree, ParameterTreeAdmin)
admin.site.register(Report, ReportAdmin)
admin.site.register(ReportVersion, ReportVersionAdmin)
admin.site.register(MainData, MainDataAdmin)
admin.site.register(AuditTable, AuditTableAdmin)
admin.site.register(MainDataProd, MainDataProdAdmin)
admin.site.register(ReportQuestion, ReportQuestionAdmin)
admin.site.register(ReportCompanies, ReportCompaniesAdmin)
