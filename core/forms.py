from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import MaintenanceRequest, Asset

class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=80, required=False)

    class Meta:
        model = User
        fields = ("username", "first_name", "email", "password1", "password2")

class MaintenanceRequestForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ("title", "asset", "asset_name", "location", "description", "priority")
        widgets = {
            "description": forms.Textarea(attrs={"rows": 4}),
            "asset": forms.Select(attrs={"class": "form-control"}),
        }
        labels = {"asset_name": "Asset name (if not in the asset list)"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["asset"].queryset = Asset.objects.filter(is_active=True)

class AssignTechnicianForm(forms.ModelForm):
    class Meta:
        model = MaintenanceRequest
        fields = ("assigned_to",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["assigned_to"].queryset = User.objects.filter(profile__role="technician", is_active=True)
        self.fields["assigned_to"].label = "Select technician"

class StatusUpdateForm(forms.ModelForm):
    TECHNICIAN_STATUSES = ("assigned", "in_progress", "resolved")

    class Meta:
        model = MaintenanceRequest
        fields = ("status", "resolution_note")
        widgets = {"resolution_note": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, role=None, **kwargs):
        super().__init__(*args, **kwargs)
        if role == "technician":
            self.fields["status"].choices = [
                c for c in MaintenanceRequest.STATUS_CHOICES if c[0] in self.TECHNICIAN_STATUSES
            ]

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("status") == "resolved" and not (cleaned.get("resolution_note") or "").strip():
            self.add_error("resolution_note", "Please add a resolution note when resolving a request.")
        return cleaned
