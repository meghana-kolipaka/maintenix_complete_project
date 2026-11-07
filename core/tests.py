from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import MaintenanceRequest


def make_user(name, role):
    u = User.objects.create_user(name, password="pass12345")
    u.profile.role = role
    u.profile.save()
    return u


class PermissionTests(TestCase):
    def setUp(self):
        self.reporter = make_user("rep", "reporter")
        self.other = make_user("other", "reporter")
        self.tech = make_user("tech", "technician")
        self.tech2 = make_user("tech2", "technician")
        self.manager = make_user("mgr", "manager")
        self.req = MaintenanceRequest.objects.create(
            title="Leaking tap", location="Block A", description="Dripping",
            reported_by=self.reporter, assigned_to=self.tech, status="assigned")

    def test_new_registration_is_reporter(self):
        self.client.post(reverse("register"), {
            "username": "newbie", "first_name": "N", "email": "n@x.com",
            "password1": "Str0ngPass!234", "password2": "Str0ngPass!234"})
        self.assertEqual(User.objects.get(username="newbie").profile.role, "reporter")

    def test_superuser_gets_admin_role(self):
        su = User.objects.create_superuser("root", "r@x.com", "pass12345")
        self.assertEqual(su.profile.role, "admin")

    def test_reporter_cannot_view_others_request(self):
        self.client.force_login(self.other)
        r = self.client.get(reverse("request_detail", args=[self.req.pk]))
        self.assertRedirects(r, reverse("request_list"))

    def test_reporter_cannot_assign(self):
        self.client.force_login(self.reporter)
        r = self.client.post(reverse("assign_request", args=[self.req.pk]), {"assigned_to": self.tech2.pk})
        self.assertRedirects(r, reverse("dashboard"))

    def test_manager_can_assign(self):
        self.client.force_login(self.manager)
        self.client.post(reverse("assign_request", args=[self.req.pk]), {"assigned_to": self.tech2.pk})
        self.req.refresh_from_db()
        self.assertEqual(self.req.assigned_to, self.tech2)

    def test_technician_cannot_update_unassigned(self):
        self.client.force_login(self.tech2)
        r = self.client.post(reverse("update_request_status", args=[self.req.pk]),
                             {"status": "resolved", "resolution_note": "x"})
        self.assertRedirects(r, reverse("request_list"))
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, "assigned")

    def test_resolving_requires_note(self):
        self.client.force_login(self.tech)
        self.client.post(reverse("update_request_status", args=[self.req.pk]),
                         {"status": "resolved", "resolution_note": ""})
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, "assigned")

    def test_technician_cannot_reject(self):
        self.client.force_login(self.tech)
        self.client.post(reverse("update_request_status", args=[self.req.pk]),
                         {"status": "rejected", "resolution_note": "no"})
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, "assigned")

    def test_technician_resolves_with_note(self):
        self.client.force_login(self.tech)
        self.client.post(reverse("update_request_status", args=[self.req.pk]),
                         {"status": "resolved", "resolution_note": "Replaced washer"})
        self.req.refresh_from_db()
        self.assertEqual(self.req.status, "resolved")


import io
import shutil
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from PIL import Image

TEMP_MEDIA = tempfile.mkdtemp()


def make_image(name="photo.png", fmt="PNG"):
    buf = io.BytesIO()
    Image.new("RGB", (10, 10), "red").save(buf, fmt)
    return SimpleUploadedFile(name, buf.getvalue(), content_type="image/png")


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class PhotoTests(TestCase):
    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def setUp(self):
        self.reporter = make_user("rep", "reporter")
        self.tech = make_user("tech", "technician")
        self.data = {"title": "Fan broken", "location": "Room 101",
                     "description": "Not rotating", "priority": "high"}

    def test_reporter_can_upload_problem_photo(self):
        self.client.force_login(self.reporter)
        self.client.post(reverse("report_issue"), {**self.data, "problem_photo": make_image()})
        req = MaintenanceRequest.objects.get(title="Fan broken")
        self.assertTrue(req.problem_photo.name.startswith("problem_photos/"))

    def test_photo_is_optional(self):
        self.client.force_login(self.reporter)
        self.client.post(reverse("report_issue"), self.data)
        self.assertTrue(MaintenanceRequest.objects.filter(title="Fan broken").exists())

    def test_wrong_file_type_rejected(self):
        self.client.force_login(self.reporter)
        bad = SimpleUploadedFile("notes.txt", b"hello", content_type="text/plain")
        self.client.post(reverse("report_issue"), {**self.data, "problem_photo": bad})
        self.assertFalse(MaintenanceRequest.objects.filter(title="Fan broken").exists())

    def test_oversized_photo_rejected(self):
        self.client.force_login(self.reporter)
        big = SimpleUploadedFile("big.png", b"0" * (5 * 1024 * 1024 + 1), content_type="image/png")
        self.client.post(reverse("report_issue"), {**self.data, "problem_photo": big})
        self.assertFalse(MaintenanceRequest.objects.filter(title="Fan broken").exists())

    def test_technician_can_upload_repair_photo(self):
        req = MaintenanceRequest.objects.create(
            title="Leak", location="A", description="d", reported_by=self.reporter,
            assigned_to=self.tech, status="assigned")
        self.client.force_login(self.tech)
        self.client.post(reverse("update_request_status", args=[req.pk]), {
            "status": "resolved", "resolution_note": "Fixed", "repair_photo": make_image("fix.png")})
        req.refresh_from_db()
        self.assertEqual(req.status, "resolved")
        self.assertTrue(req.repair_photo.name.startswith("repair_photos/"))
