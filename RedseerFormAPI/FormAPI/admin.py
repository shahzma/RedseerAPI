from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ReportVersion, AuditTable

# Register your models here.
admin.site.register(ReportVersion)
admin.site.register(AuditTable)