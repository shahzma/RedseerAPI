from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Sector, Industry, Player, Parameter, ParameterTree, Report, ReportVersion, MainData, AuditTable, MainDataProd, ReportQuestion


class SectorAdmin(admin.ModelAdmin):
    list_display = ('sector_id', 'sector_name')
    ordering = ('sector_id',)
    search_fields = ['sector_name']


class IndustryAdmin(admin.ModelAdmin):
    list_display = ('industry_id', 'industry_name', 'sector_name')
    ordering = ('industry_id',)
    search_fields = ['industry_name', 'sector_name']


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('player_id', 'player_name', 'industry')
    ordering = ('player_id',)
    search_fields = ['player_name', 'industry__industry_name']


class ParameterAdmin(admin.ModelAdmin):
    list_display = ('parameter_id', 'parameter_name')
    ordering = ('parameter_id',)
    search_fields = ['parameter_name']


class ParameterTreeAdmin(admin.ModelAdmin):
    list_display = ('id', 'question')
    ordering = ('id',)
    search_fields = ['question']


class ReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    ordering = ('id',)
    search_fields = ['name']


class ReportVersionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'company')
    ordering = ('id',)
    search_fields = ['company']


class MainDataAdmin(admin.ModelAdmin):
    list_display = ('id', 'player', 'start_date',
                    'parametertree', 'report_version')
    ordering = ('-start_date',)
    search_fields = ['start_date',
                     'parametertree__question', 'report_version__name']


class AuditTableAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_level', 'form_id')
    ordering = ('user_level',)
    search_fields = ['user', 'form_id__name']


class MainDataProdAdmin(admin.ModelAdmin):
    list_display = ('id', 'player', 'start_date',
                    'parametertree', 'report_version')
    ordering = ('-start_date',)
    search_fields = ['start_date',
                     'parametertree__question', 'report_version__name']


class ReportQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'report', 'parametertree', 'sequence')
    ordering = ('id',)
    search_fields = ['report__name', 'parametertree__question']


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
