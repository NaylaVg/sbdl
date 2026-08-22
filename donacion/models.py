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


class Donacion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor_code = models.CharField(max_length=20, null=False, unique=True)
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False)
    dni = models.CharField(max_length=20, null=False, unique=True)
    phone = models.CharField(max_length=20, null=False)
    address = models.TextField(null=False)
    blood_type = models.CharField(max_length=5, null=False)
    serology_status = models.CharField(max_length=20, null=False, default='pending')
    serology_date = models.DateField(null=True, blank=True)
    serology_result = models.TextField(null=True, blank=True)
    medical_notes = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=20, null=False, default='pending')
    center_id = models.ForeignKey(CollectionCenter, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Visit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    donor = models.ForeignKey(Donacion, on_delete=models.PROTECT)
    visit_date = models.DateTimeField(null=False)
    volume_raw_ml = models.DecimalField(max_digits=8, decimal_places=2)
    responsible = models.CharField(max_length=100, null=False)
    center_id = models.ForeignKey(CollectionCenter, on_delete=models.PROTECT)
    notes = models.TextField(null=True, blank=True)
    next_visit_due = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
