import uuid
from django.db import models


class MilkStage(models.TextChoices):
    COLOSTRUM = 'colostrum', 'Calostro'
    TRANSITION = 'transition', 'Transición'
    MATURE_LOW = 'mature_low', 'Madura baja'
    MATURE_HIGH = 'mature_high', 'Madura alta'


class TargetType(models.TextChoices):
    PRETERM = 'preterm', 'Prematuro'
    TERM = 'term', 'Término'


class CultureResult(models.TextChoices):
    PENDING = 'pending', 'Pending'
    NEGATIVE = 'negative', 'Negative'
    POSITIVE = 'positive', 'Positive'


class MilkBatches(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    barcode = models.CharField(max_length=30, null=False, unique=True)
    batch_number = models.IntegerField(null=False)
    donor_id = models.ForeignKey('donacion.Donacion', on_delete=models.PROTECT, null=False)
    center_id = models.ForeignKey('donacion.CollectionCenter', on_delete=models.PROTECT, null=False)
    collection_date = models.DateTimeField(null=False)
    volume_ml = models.DecimalField(max_digits=8, decimal_places=2, null=False)
    milk_stage = models.CharField(max_length=20, null=False, choices=MilkStage.choices)
    target = models.CharField(max_length=20, null=False, choices=TargetType.choices)
    calories_kcal = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, null=False, default='raw')
    storage_temp = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    expiration_date = models.DateField(null=False)
    responsible = models.CharField(max_length=100, null=False)
    visit_id = models.ForeignKey('donacion.Visit', on_delete=models.PROTECT, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Milk Batches"

    def __str__(self):
        return f"{self.milk_stage} - {self.batch_number}"


class PasteurizationRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    batch_id = models.ForeignKey(MilkBatches, on_delete=models.PROTECT, null=False)
    new_barcode = models.CharField(max_length=30, null=False, unique=True)
    pasteurization_date = models.DateTimeField(null=False)
    method = models.CharField(max_length=20, null=False)
    temp_celsius = models.DecimalField(max_digits=5, decimal_places=2, null=False)
    duration_min = models.IntegerField(null=False)
    volume_ml = models.DecimalField(max_digits=8, decimal_places=2, null=False)
    milk_stage = models.CharField(max_length=20, null=False, choices=MilkStage.choices)
    target = models.CharField(max_length=20, null=False, choices=TargetType.choices)
    calories_kcal = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    acidity_dornic = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    cream_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    fat_pct = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    kcal_per_liter = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    culture_24h_result = models.CharField(max_length=20, null=False, choices=CultureResult.choices, default=CultureResult.PENDING)
    culture_24h_date = models.DateField(null=True, blank=True)
    culture_48h_result = models.CharField(max_length=20, null=False, choices=CultureResult.choices, default=CultureResult.PENDING)
    culture_48h_date = models.DateField(null=True, blank=True)
    quality_result = models.CharField(max_length=20, null=False, default='pending')
    bacterial_count = models.IntegerField(null=True, blank=True)
    responsible = models.CharField(max_length=100, null=False)
    discarded = models.BooleanField(null=False, default=False)
    discard_reason = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Lote {self.batch_id.batch_number} - {self.method}"


class Fractionation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fractionation_number = models.CharField(max_length=20, null=False, unique=True)
    pasteurization_id = models.ForeignKey(PasteurizationRecord, on_delete=models.PROTECT, null=False, related_name='fractionations')
    fractionation_date = models.DateTimeField(null=False)
    total_volume_ml = models.DecimalField(max_digits=8, decimal_places=2, null=False)
    responsible = models.CharField(max_length=100, null=False)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.fractionation_number


class FractionatedBottle(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        RESERVED = 'reserved', 'Reserved'
        USED = 'used', 'Used'
        DISCARDED = 'discarded', 'Discarded'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qr_code = models.CharField(max_length=30, null=False, unique=True)
    fractionation_id = models.ForeignKey(Fractionation, on_delete=models.PROTECT, null=False, related_name='bottles')
    volume_ml = models.DecimalField(max_digits=8, decimal_places=2, null=False)
    milk_stage = models.CharField(max_length=20, null=False, choices=MilkStage.choices)
    target = models.CharField(max_length=20, null=False, choices=TargetType.choices)
    calories_kcal = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    expiration_date = models.DateField(null=False)
    status = models.CharField(max_length=20, null=False, choices=Status.choices, default=Status.AVAILABLE)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Fractionated Bottles"

    def __str__(self):
        return self.qr_code


class DonorDismissal(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor_id = models.ForeignKey('donacion.Donacion', on_delete=models.PROTECT, null=False)
    dismissal_date = models.DateTimeField(null=False)
    reason = models.TextField(null=False)
    dismissed_by = models.CharField(max_length=100, null=False)
    can_reenter = models.BooleanField(null=False, default=False)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor_id} - {self.dismissed_by}"


class InternalExtraction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor_id = models.ForeignKey('donacion.Donacion', on_delete=models.PROTECT, null=False)
    patient_id = models.ForeignKey('nutricion.Patient', on_delete=models.PROTECT, null=True, blank=True)
    extraction_date = models.DateTimeField(null=False)
    scheduled_time = models.TimeField(null=True, blank=True)
    volume_ml = models.DecimalField(max_digits=8, decimal_places=2, null=False)
    used_immediately = models.BooleanField(null=False, default=False)
    frozen = models.BooleanField(null=True, blank=True, default=False)
    batch_id = models.ForeignKey(MilkBatches, on_delete=models.PROTECT, null=True, blank=True)
    responsible = models.CharField(max_length=100, null=False)
    extraction_staff_id = models.ForeignKey('auditoria.Staff', on_delete=models.PROTECT, null=False)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.patient_id:
            return f"{self.donor_id} - {self.patient_id} - {self.extraction_date}"
        return f"{self.donor_id} - {self.extraction_date}"
