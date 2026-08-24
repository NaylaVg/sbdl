from django.contrib import admin
from .models import Formula, StockEntry, StockExit, StockAlert

admin.site.register(Formula)
admin.site.register(StockEntry)
admin.site.register(StockExit)
admin.site.register(StockAlert)