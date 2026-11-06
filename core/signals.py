from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Profile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    profile, _ = Profile.objects.get_or_create(user=instance)
    # Superusers created with createsuperuser automatically get the admin role
    if instance.is_superuser and profile.role == "reporter":
        profile.role = "admin"
        profile.save()
