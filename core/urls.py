from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register_view, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("requests/", views.request_list, name="request_list"),
    path("requests/new/", views.report_issue, name="report_issue"),
    path("requests/<int:pk>/", views.request_detail, name="request_detail"),
    path("requests/<int:pk>/assign/", views.assign_request, name="assign_request"),
    path("requests/<int:pk>/update/", views.update_request_status, name="update_request_status"),
]
