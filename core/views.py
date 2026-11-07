from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from .decorators import roles_required
from .forms import RegisterForm, MaintenanceRequestForm, AssignTechnicianForm, StatusUpdateForm
from .models import Asset, MaintenanceRequest


def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email = form.cleaned_data["email"]
            user.first_name = form.cleaned_data["first_name"]
            user.save()
            login(request, user)
            messages.success(request, "Your reporter account has been created.")
            return redirect("dashboard")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    role = request.user.profile.role
    requests_qs = MaintenanceRequest.objects.select_related("reported_by", "assigned_to", "asset")
    if role == "reporter":
        requests_qs = requests_qs.filter(reported_by=request.user)
    elif role == "technician":
        requests_qs = requests_qs.filter(assigned_to=request.user)

    context = {
        "role": role,
        "total_count": requests_qs.count(),
        "pending_count": requests_qs.filter(status="pending").count(),
        "active_count": requests_qs.filter(status__in=["assigned", "in_progress"]).count(),
        "resolved_count": requests_qs.filter(status="resolved").count(),
        "recent_requests": requests_qs[:8],
        "asset_count": Asset.objects.filter(is_active=True).count(),
        "technicians": User.objects.filter(profile__role="technician", is_active=True),
    }
    return render(request, "core/dashboard.html", context)


@login_required
def request_list(request):
    role = request.user.profile.role
    qs = MaintenanceRequest.objects.select_related("reported_by", "assigned_to", "asset")
    if role == "reporter":
        qs = qs.filter(reported_by=request.user)
    elif role == "technician":
        qs = qs.filter(assigned_to=request.user)

    status = request.GET.get("status", "")
    query = request.GET.get("q", "").strip()
    if status:
        qs = qs.filter(status=status)
    if query:
        qs = qs.filter(Q(title__icontains=query) | Q(location__icontains=query) |
                       Q(asset_name__icontains=query) | Q(description__icontains=query))
    return render(request, "core/request_list.html", {"requests": qs, "status": status, "query": query})


@login_required
def report_issue(request):
    if request.method == "POST":
        form = MaintenanceRequestForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.reported_by = request.user
            if obj.asset:
                obj.location = obj.location or obj.asset.location
            obj.save()
            messages.success(request, f"Request #{obj.pk} submitted successfully.")
            return redirect("request_list")
    else:
        form = MaintenanceRequestForm()
    return render(request, "core/form_page.html", {
        "form": form, "page_title": "Report a maintenance issue",
        "button_text": "Submit request"
    })


@login_required
@roles_required("manager", "admin")
def assign_request(request, pk):
    obj = get_object_or_404(MaintenanceRequest, pk=pk)
    if request.method == "POST":
        form = AssignTechnicianForm(request.POST, instance=obj)
        if form.is_valid():
            item = form.save(commit=False)
            item.status = "assigned"
            item.save()
            messages.success(request, "Technician assigned successfully.")
            return redirect("request_list")
    else:
        form = AssignTechnicianForm(instance=obj)
    return render(request, "core/form_page.html", {
        "form": form, "page_title": f"Assign technician – Request #{obj.pk}",
        "button_text": "Assign technician", "object": obj
    })


@login_required
@roles_required("technician", "manager", "admin")
def update_request_status(request, pk):
    obj = get_object_or_404(MaintenanceRequest, pk=pk)
    if request.user.profile.role == "technician" and obj.assigned_to_id != request.user.id:
        messages.error(request, "This request is not assigned to you.")
        return redirect("request_list")
    if request.method == "POST":
        form = StatusUpdateForm(request.POST, request.FILES, instance=obj, role=request.user.profile.role)
        if form.is_valid():
            form.save()
            messages.success(request, "Request status updated.")
            return redirect("request_list")
    else:
        form = StatusUpdateForm(instance=obj, role=request.user.profile.role)
    return render(request, "core/form_page.html", {
        "form": form, "page_title": f"Update request #{obj.pk}",
        "button_text": "Save update", "object": obj
    })


@login_required
def request_detail(request, pk):
    obj = get_object_or_404(
        MaintenanceRequest.objects.select_related("reported_by", "assigned_to", "asset"), pk=pk
    )
    role = request.user.profile.role
    if role == "reporter" and obj.reported_by_id != request.user.id:
        messages.error(request, "You cannot view this request.")
        return redirect("request_list")
    if role == "technician" and obj.assigned_to_id != request.user.id:
        messages.error(request, "You cannot view this request.")
        return redirect("request_list")
    return render(request, "core/request_detail.html", {"item": obj})
