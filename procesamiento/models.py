import uuid
from django.db import models


class MilkBatches(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    barcode = models.CharField(max_length=30, null=False, unique=True)
    batch_number = models.IntegerField(null=False)
    donor_id = models.ForeignKey('donacion.Donacion', on_delete=models.PROTECT)
    center_id = models.ForeignKey('donacion.CollectionCenter', on_delete=models.PROTECT)
    collection_date = models.DateTimeField(null=False)
    volume_ml = models.DecimalField(max_digits=8, decimal_places=2, null=False)
    milk_type = models.CharField(max_length=20, null=False)
    calories_kcal = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=20, null=False, default='raw')
    storage_temp = models.DecimalField(max_digits=4, decimal_places=1)
    expiration_date = models.DateField(null=False)
    responsible = models.CharField(max_length=100, null=False)
    visit_id = models.ForeignKey('donacion.Visit', on_delete=models.PROTECT)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class PasteurizationRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch_id = models.ForeignKey(MilkBatches, on_delete=models.PROTECT)
    new_barcode = models.CharField(max_length=30, null=False, unique=True)
    pasteurization_date = models.DateTimeField(null=False)
    method = models.CharField(max_length=20, null=False)
    temp_celsius = models.DecimalField(max_digits=5, decimal_places=2, null=False)
    duration_min = models.IntegerField(null=False)
    volume_ml = models.DecimalField(max_digits=8, decimal_places=2, null=False)
    milk_type = models.CharField(max_length=20, null=False)
    calories_kcal = models.DecimalField(max_digits=6, decimal_places=2)
    quality_result = models.CharField(max_length=20, default='pending')
    bacterial_count = models.IntegerField(null=True, blank=True)
    responsible = models.CharField(max_length=100, null=False)
    discarded = models.BooleanField(default=False, null=False)
    discard_reason = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class DonorDismissal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor_id = models.ForeignKey('donacion.Donacion', on_delete=models.PROTECT)
    dismissal_date = models.DateTimeField(null=False)
    reason = models.TextField(null=False)
    dismissed_by = models.CharField(max_length=100, null=False)
    can_reenter = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class InternalExtraction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor_id = models.ForeignKey('donacion.Donacion', on_delete=models.PROTECT)
    patient_id = models.ForeignKey('nutricion.Patient', on_delete=models.PROTECT)
    extraction_date = models.DateTimeField(null=False)
    scheduled_time = models.TimeField()
    volume_ml = models.DecimalField(max_digits=8, decimal_places=2, null=False)
    used_immediately = models.BooleanField(default=False)
    frozen = models.BooleanField(default=False, null=True)
    batch_id = models.ForeignKey(MilkBatches, on_delete=models.PROTECT, null=True, blank=True)
    responsible = models.CharField(max_length=100, null=False)
    extraction_staff_id = models.ForeignKey('auditoria.Staff', on_delete=models.PROTECT, null=False)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
