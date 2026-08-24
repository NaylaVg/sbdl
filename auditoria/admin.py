from django.contrib import admin
from .models import Staff, DailyAssignment, AuditLog

admin.site.register(Staff)
admin.site.register(DailyAssignment)
admin.site.register(AuditLog)