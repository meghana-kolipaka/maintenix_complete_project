from django.contrib import admin
from .models import Profile, Asset, MaintenanceRequest

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    list_filter = ("role",)
    search_fields = ("user__username", "user__email")

@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ("name", "asset_code", "category", "location", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "asset_code", "location")

@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "reported_by", "assigned_to", "priority", "status", "created_at")
    list_filter = ("status", "priority")
    search_fields = ("title", "description", "location", "asset_name")
