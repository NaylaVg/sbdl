import uuid
from django.db import models
from procesamiento.models import MilkStage, TargetType


class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_code = models.CharField(max_length=20, null=False, unique=True)
    first_name = models.CharField(max_length=100, null=False)
    birth_date = models.DateField(null=False)
    birth_weight_g = models.IntegerField(null=True, blank=True)
    gestational_age_weeks = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    sex = models.CharField(max_length=1, null=False)
    diagnosis = models.TextField(null=True, blank=True)
    mother_id = models.ForeignKey('donacion.Donacion', on_delete=models.PROTECT, null=True, blank=True)
    admission_date = models.DateField(null=False)
    discharge_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, null=False, default='active')
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.first_name


class FeedingPlan(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.ForeignKey(Patient, on_delete=models.PROTECT)
    formula_id = models.ForeignKey('inventario.Formula', on_delete=models.PROTECT, null=True, blank=True)
    milk_stage = models.CharField(max_length=20, null=True, blank=True, choices=MilkStage.choices)
    target = models.CharField(max_length=20, null=True, blank=True, choices=TargetType.choices)
    feeding_type = models.CharField(max_length=30, null=False)
    volume_ml_per_feed = models.DecimalField(max_digits=6, decimal_places=2, null=False)
    feeds_per_day = models.IntegerField(null=False)
    total_daily_ml = models.DecimalField(max_digits=8, decimal_places=2, null=False)
    calories_target = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=True, blank=True)
    prescribed_by = models.CharField(max_length=100, null=False)
    status = models.CharField(max_length=20, null=False, default='active')
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_id} - {self.feeding_type}"


class NutritionTracking(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient_id = models.ForeignKey(Patient, on_delete=models.PROTECT)
    measurement_date = models.DateField(null=False)
    age_days = models.IntegerField(null=False)
    weight_g = models.IntegerField(null=True, blank=True)
    height_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    head_circumference_cm = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    bmi = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight_percentile_oms = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    height_percentile_oms = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    daily_intake_ml = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    daily_kcal = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    feeding_plan_id = models.ForeignKey(FeedingPlan, on_delete=models.PROTECT, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    recorded_by = models.CharField(max_length=100, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.patient_id} - {self.measurement_date}"
