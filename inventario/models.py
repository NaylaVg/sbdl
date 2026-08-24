import uuid
from django.db import models
from procesamiento.models import MilkStage, TargetType


class Formula(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, null=False)
    brand = models.CharField(max_length=100, null=False)
    type = models.CharField(max_length=30, null=False)
    presentation = models.CharField(max_length=50, null=True, blank=True)
    unit_measure = models.CharField(max_length=20, null=False)
    calories_kcal_per_unit = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    min_stock_alert = models.IntegerField(null=False, default=10)
    requires_prescription = models.BooleanField(null=False, default=False)
    is_active = models.BooleanField(null=False, default=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class StockEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    formula_id = models.ForeignKey(Formula, on_delete=models.PROTECT, null=True, blank=True)
    fractionated_bottle_id = models.ForeignKey('procesamiento.FractionatedBottle', on_delete=models.PROTECT, null=True, blank=True)
    entry_type = models.CharField(max_length=30, null=False)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    unit_measure = models.CharField(max_length=20, null=False)
    lot_number = models.CharField(max_length=30, null=True, blank=True)
    manufacturing_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=False)
    supplier = models.CharField(max_length=100, null=True, blank=True)
    purchase_order = models.CharField(max_length=50, null=True, blank=True)
    milk_stage = models.CharField(max_length=20, null=True, blank=True, choices=MilkStage.choices)
    target = models.CharField(max_length=20, null=True, blank=True, choices=TargetType.choices)
    calories_kcal = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    entry_date = models.DateTimeField(null=False)
    responsible = models.CharField(max_length=100, null=False)
    pharmacy_request_date = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.entry_type} - {self.entry_date}"


class StockExit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stock_entry_id = models.ForeignKey(StockEntry, on_delete=models.PROTECT, null=False)
    exit_type = models.CharField(max_length=30, null=False)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    unit_measure = models.CharField(max_length=20, null=False)
    exit_date = models.DateTimeField(null=False)
    patient_id = models.ForeignKey('nutricion.Patient', on_delete=models.PROTECT, null=True, blank=True)
    reason = models.CharField(max_length=30, null=False)
    responsible = models.CharField(max_length=100, null=False)
    center_id = models.ForeignKey('donacion.CollectionCenter', on_delete=models.PROTECT, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exit_type} - {self.exit_date}"


class StockAlert(models.Model):
    class Severity(models.TextChoices):
        INFO = 'info', 'Info'
        WARNING = 'warning', 'Warning'
        CRITICAL = 'critical', 'Critical'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert_type = models.CharField(max_length=30, null=False)
    entity_type = models.CharField(max_length=50, null=False)
    entity_id = models.UUIDField(null=False)
    severity = models.CharField(max_length=20, null=False, choices=Severity.choices)
    message = models.TextField(null=False)
    is_acknowledged = models.BooleanField(null=False, default=False)
    acknowledged_by = models.CharField(max_length=100, null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.alert_type} - {self.severity}"
