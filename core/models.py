from django.conf import settings
from django.db import models
from .validators import validate_photo


class Profile(models.Model):
    ROLE_CHOICES = [
        ("reporter", "Reporter"),
        ("technician", "Technician"),
        ("manager", "Manager"),
        ("admin", "Admin"),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="reporter")

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Asset(models.Model):
    name = models.CharField(max_length=120)
    asset_code = models.CharField(max_length=40, unique=True)
    category = models.CharField(max_length=80)
    location = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.asset_code})"


class MaintenanceRequest(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("assigned", "Assigned"),
        ("in_progress", "In Progress"),
        ("resolved", "Resolved"),
        ("rejected", "Rejected"),
    ]
    PRIORITY_CHOICES = [
        ("low", "Low"),
        ("medium", "Medium"),
        ("high", "High"),
        ("urgent", "Urgent"),
    ]

    title = models.CharField(max_length=150)
    asset = models.ForeignKey(Asset, on_delete=models.SET_NULL, null=True, blank=True,
                              related_name="requests")
    asset_name = models.CharField(max_length=120, blank=True)
    location = models.CharField(max_length=120)
    description = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default="medium")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default="pending")
    reported_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                    related_name="reported_requests")
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name="assigned_requests")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolution_note = models.TextField(blank=True)
    problem_photo = models.ImageField(upload_to="problem_photos/", blank=True, null=True,
                                      validators=[validate_photo])
    repair_photo = models.ImageField(upload_to="repair_photos/", blank=True, null=True,
                                     validators=[validate_photo])

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"#{self.pk} - {self.title}"

    def save(self, *args, **kwargs):
        if self.asset and not self.asset_name:
            self.asset_name = self.asset.name
        super().save(*args, **kwargs)
