from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from core.models import Asset, MaintenanceRequest


class Command(BaseCommand):
    help = "Create demo users (reporter/technician/manager), assets and sample requests."

    def handle(self, *args, **opts):
        users = {}
        for name, role in [("reporter1", "reporter"), ("tech1", "technician"), ("manager1", "manager")]:
            u, created = User.objects.get_or_create(username=name, defaults={"email": f"{name}@example.com"})
            if created:
                u.set_password("demo12345")
                u.save()
            u.profile.role = role
            u.profile.save()
            users[role] = u
        assets = [Asset.objects.get_or_create(asset_code=c, defaults=dict(name=n, category=cat, location=loc))[0]
                  for c, n, cat, loc in [("AC-001", "Split AC Unit", "HVAC", "Block A, Room 101"),
                                         ("PR-014", "Projector", "Electronics", "Seminar Hall"),
                                         ("WP-007", "Water Purifier", "Plumbing", "Cafeteria")]]
        if not MaintenanceRequest.objects.exists():
            MaintenanceRequest.objects.create(title="AC not cooling", asset=assets[0], location=assets[0].location,
                description="Blowing warm air since morning.", priority="high", reported_by=users["reporter"])
            MaintenanceRequest.objects.create(title="Projector flickering", asset=assets[1], location=assets[1].location,
                description="Display flickers every few minutes.", priority="medium", reported_by=users["reporter"],
                assigned_to=users["technician"], status="assigned")
        self.stdout.write(self.style.SUCCESS("Demo data ready. Logins: reporter1 / tech1 / manager1, password demo12345"))
