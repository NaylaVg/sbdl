import uuid
from django.db import models


class Staff(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee_code = models.CharField(max_length=10, null=False, unique=True)
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=False)
    role = models.CharField(max_length=30, null=False)
    email = models.CharField(max_length=150, unique=True, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    center_id = models.ForeignKey('donacion.CollectionCenter', on_delete=models.PROTECT, null=True, blank=True)
    is_active = models.BooleanField(null=False, default=True)
    last_login = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class DailyAssignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment_date = models.DateField(null=False)
    staff_id = models.ForeignKey(Staff, on_delete=models.PROTECT, null=False)
    center_id = models.ForeignKey('donacion.CollectionCenter', on_delete=models.PROTECT, null=False)
    role_day = models.CharField(max_length=30, null=False)
    shift = models.CharField(max_length=20, null=False)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.assignment_date} - {self.shift}"


class AuditLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(null=False)
    staff_id = models.ForeignKey(Staff, on_delete=models.PROTECT, null=True, blank=True)
    action = models.CharField(max_length=30, null=False)
    entity_type = models.CharField(max_length=50, null=False)
    entity_id = models.UUIDField(null=False)
    old_values = models.JSONField(null=True, blank=True)
    new_values = models.JSONField(null=True, blank=True)
    ip_address = models.CharField(max_length=45, null=True, blank=True)
    device_info = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.action} - {self.entity_type}"