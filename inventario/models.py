import uuid
from django.db import models


class Formula(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150, null=False)
    brand = models.CharField(max_length=100)
    type = models.CharField(max_length=30, null=False)
    presentation = models.CharField(max_length=50)
    unit_measure = models.CharField(max_length=20, null=False)
    calories_kcal_per_unit = models.DecimalField(max_digits=6, decimal_places=2)
    min_stock_alert = models.IntegerField(null=False, default=10)
    requires_prescription = models.BooleanField(null=False, default=False)
    is_active = models.BooleanField(null=False, default=True)
    notes = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class StockEntry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    formula_id = models.ForeignKey(Formula, on_delete=models.PROTECT, null=True, blank=True)
    pasteurization_id = models.ForeignKey('procesamiento.PasteurizationRecord', on_delete=models.PROTECT, null=True, blank=True)
    entry_type = models.CharField(max_length=30, null=False)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    unit_measure = models.CharField(max_length=20, null=False)
    lot_number = models.CharField(max_length=30, null=True, blank=True)
    manufacturing_date = models.DateField(null=True, blank=True)
    expiration_date = models.DateField(null=False)
    supplier = models.CharField(max_length=100, null=True, blank=True)
    purchase_order = models.CharField(max_length=50, null=True, blank=True)
    entry_date = models.DateTimeField(null=False)
    responsible = models.CharField(max_length=100, null=False)
    pharmacy_request_date = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class StockExit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    stock_entry_id = models.ForeignKey(StockEntry, on_delete=models.PROTECT)
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


class StockAlert(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    alert_type = models.CharField(max_length=30, null=False)
    entity_type = models.CharField(max_length=50, null=False)
    entity_id = models.UUIDField(null=False)
    severity = models.CharField(max_length=20, null=False)
    message = models.TextField(null=False)
    is_acknowledged = models.BooleanField(default=False, null=False)
    acknowledged_by = models.CharField(max_length=100, null=True, blank=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
