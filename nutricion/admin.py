from django.contrib import admin
from .models import Patient, FeedingPlan, NutritionTracking

admin.site.register(Patient)
admin.site.register(FeedingPlan)
admin.site.register(NutritionTracking)