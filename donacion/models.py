import uuid
from django.db import models


class CollectionCenter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=10, null=False, unique=True)
    name = models.CharField(max_length=100, null=False)
    address = models.TextField(null=False)
    phone = models.CharField(max_length=20, null=False)
    responsible = models.CharField(max_length=100, null=False)
    is_active = models.BooleanField(null=False, default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Zone(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, null=False, unique=True)
    center_id = models.ForeignKey(CollectionCenter, on_delete=models.PROTECT, null=False)
    monday = models.BooleanField(null=False, default=False)
    tuesday = models.BooleanField(null=False, default=False)
    wednesday = models.BooleanField(null=False, default=False)
    thursday = models.BooleanField(null=False, default=False)
    friday = models.BooleanField(null=False, default=False)
    is_active = models.BooleanField(null=False, default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Zones"


class Donacion(models.Model):
    class SerologyStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        OK = 'ok', 'Ok'
        REJECTED = 'rejected', 'Rejected'

    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        ACTIVE = 'active', 'Active'
        SUSPENDED = 'suspended', 'Suspended'
        DISMISSED = 'dismissed', 'Dismissed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor_code = models.CharField(max_length=20, null=False, unique=True)
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False)
    dni = models.CharField(max_length=20, null=False, unique=True)
    phone = models.CharField(max_length=20, null=False)
    email = models.CharField(max_length=150, null=True, blank=True)
    address = models.TextField(null=False)
    blood_type = models.CharField(max_length=5, null=False)
    serology_status = models.CharField(max_length=20, null=False, choices=SerologyStatus.choices, default=SerologyStatus.PENDING)
    medical_notes = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, null=False, choices=Status.choices, default=Status.PENDING)
    center_id = models.ForeignKey(CollectionCenter, on_delete=models.PROTECT, null=False)
    zone_id = models.ForeignKey(Zone, on_delete=models.PROTECT, null=True, blank=True)
    baby_birth_date = models.DateField(null=True, blank=True)
    baby_gestational_age_weeks = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    baby_birth_weight_g = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class SerologyStudy(models.Model):
    class StudyType(models.TextChoices):
        HIV = 'hiv', 'HIV'
        HEP_B = 'hep_b', 'Hepatitis B'
        HEP_C = 'hep_c', 'Hepatitis C'
        HTLV = 'htlv_i_ii', 'HTLV I/II'
        TOXOPLASMOSIS = 'toxoplasmosis', 'Toxoplasmosis'
        CHAGAS = 'chagas', 'Chagas'
        VDRL = 'vdrl', 'VDRL'

    class Result(models.TextChoices):
        PENDING = 'pending', 'Pending'
        OK = 'ok', 'Ok'
        REJECTED = 'rejected', 'Rejected'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor_id = models.ForeignKey(Donacion, on_delete=models.PROTECT, null=False, related_name='serology_studies')
    study_type = models.CharField(max_length=20, null=False, choices=StudyType.choices)
    result = models.CharField(max_length=20, null=False, choices=Result.choices, default=Result.PENDING)
    sample_date = models.DateField(null=True, blank=True)
    result_date = models.DateField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor_id} - {self.study_type} - {self.result}"


class Consent(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        CLOSED = 'closed', 'Closed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    consent_number = models.CharField(max_length=20, null=False, unique=True)
    donor_id = models.ForeignKey(Donacion, on_delete=models.PROTECT, null=False, related_name='consents')
    signature_date = models.DateField(null=False)
    address = models.TextField(null=False)
    bottles_to_print = models.IntegerField(null=False)
    serology_requested = models.BooleanField(null=False, default=True)
    photo_permission = models.BooleanField(null=False, default=False)
    status = models.CharField(max_length=20, null=False, choices=Status.choices, default=Status.ACTIVE)
    end_date = models.DateField(null=True, blank=True)
    end_reason = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.consent_number} - {self.donor_id}"


class Visit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor = models.ForeignKey(Donacion, on_delete=models.PROTECT, null=False)
    visit_date = models.DateTimeField(null=False)
    volume_raw_ml = models.DecimalField(max_digits=8, decimal_places=2, null=False)
    responsible_id = models.ForeignKey('auditoria.Staff', on_delete=models.PROTECT, null=False)
    center_id = models.ForeignKey(CollectionCenter, on_delete=models.PROTECT, null=False)
    notes = models.TextField(null=True, blank=True)
    next_visit_due = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.visit_date)
