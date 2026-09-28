import datetime
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from main.forms import ExperienceForm, ProjectForm
from main.models import Education, Experience, Project
from django.contrib.auth.decorators import login_required  
from django.core.exceptions import PermissionDenied        


def register(request):
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Akun berhasil dibuat. Silakan login.")
        return redirect("main:login")

    context = {
        "name": "Muhammad Sabri",
        "form": form,
    }
    return render(request, "register.html", context)


def login_user(request):
    form = AuthenticationForm(request, data=request.POST or None)

    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        response = redirect("main:show_main")
        response.set_cookie('last_login', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        return response

    context = {
        "name": "Burhan",
        "form": form,
    }
    return render(request, "login.html", context)

def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie('last_login')
    return response

def show_main(request):
    last_login = request.COOKIES.get('last_login', 'Belum ada sesi login / Cookie tidak ditemukan')
    context = {
        "name": "Burhan",
        "npm": "2206000000",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Mahasiswa Ilmu Komputer Universitas Indonesia yang tertarik "
            "pada pengembangan perangkat lunak dan pendidikan."
        ),
        "last_login": last_login,
    }
    return render(request, "index.html", context)

def get_experience_json(request):
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.all()
    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    experience_json = serializers.serialize("json", experiences)
    return HttpResponse(experience_json, content_type="application/json")


def get_experience_xml(request):
    title_query = request.GET.get("title", "").strip()
    experiences = Experience.objects.all()
    if title_query:
        experiences = experiences.filter(title__icontains=title_query)

    experience_xml = serializers.serialize("xml", experiences)
    return HttpResponse(experience_xml, content_type="application/xml")


def get_experience_json_by_id(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    experience_json = serializers.serialize("json", [experience])
    return HttpResponse(experience_json, content_type="application/json")


def get_experience_xml_by_id(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    experience_xml = serializers.serialize("xml", [experience])
    return HttpResponse(experience_xml, content_type="application/xml")


def show_experience(request):
    json_response = get_experience_json(request)
    experiences = serializers.deserialize(
        "json", json_response.content.decode("utf-8")
    )
    experience_list = [experience.object for experience in experiences]

    title_query = request.GET.get("title", "").strip()
    context = {
        "name": "Muhammad Sabri",
        "experience_list": experience_list,
        "title_query": title_query,
    }
    return render(request, "experience.html", context)


def create_experience(request):
    form = ExperienceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman baru berhasil ditambahkan!")
        return redirect("main:show_experience")

    context = {
        "name": "Muhammad Sabri",
        "form": form,
    }
    return render(request, "experience_form.html", context)


def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    if request.method == "POST":
        experience.delete()
        messages.success(request, "Pengalaman berhasil dihapus!")
    return redirect("main:show_experience")


def show_experience_detail(request, id):
    context = {
        "name": "Muhammad Sabri",
        "experience": get_object_or_404(Experience, id=id),
    }
    return render(request, "experience_detail.html", context)


def show_education(request):
    context = {
        "name": "Muhammad Sabri",
        "education_list": Education.objects.all(),
    }
    return render(request, "education.html", context)


def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_json = serializers.serialize("json", projects)
    return HttpResponse(projects_json, content_type="application/json")


def get_projects_xml(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)

    projects_xml = serializers.serialize("xml", projects)
    return HttpResponse(projects_xml, content_type="application/xml")


def get_project_json_by_id(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project_json = serializers.serialize("json", [project])
    return HttpResponse(project_json, content_type="application/json")


def get_project_xml_by_id(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    project_xml = serializers.serialize("xml", [project])
    return HttpResponse(project_xml, content_type="application/xml")


def show_projects(request):
    json_response = get_projects_json(request)
    projects = serializers.deserialize(
        "json", json_response.content.decode("utf-8")
    )
    project_list = [project.object for project in projects]

    title_query = request.GET.get("title", "").strip()
    context = {
        "name": "Muhammad Sabri",
        "project_list": project_list,
        "title_query": title_query,
    }
    return render(request, "project.html", context)

@login_required(login_url="/login/")
def create_project(request):
    if not request.user.is_superuser:
        raise PermissionDenied
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")

    context = {
        "name": "Muhammad Sabri",
        "form": form,
    }
    return render(request, "projects_form.html", context)

@login_required(login_url="/login/")
def delete_project(request, project_id):
    if not request.user.is_superuser:
        raise PermissionDenied
    project = get_object_or_404(Project, pk=project_id)
    if request.method == "POST":
        project.delete()
        messages.success(request, "Project berhasil dihapus!")
        return redirect("main:show_projects")
    return redirect("main:show_projects")


def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek berhasil diperbarui!")
        return redirect("main:show_projects")

    context = {
        "name": "Muhammad Sabri",
        "form": form,
        "project": project,
    }
    return render(request, "projects_edit.html", context)

# Tanpa cek is_superuser: semua akun yang sudah login boleh memberi star
@login_required(login_url="/login/")
def toggle_star(request, project_id):
    project = get_object_or_404(Project, pk=project_id)

    if request.method == "POST":
        # Kalau akun ini sudah pernah memberi star, batalkan star-nya.
        # Kalau belum, tambahkan star.
        if request.user in project.starred_by.all():
            project.starred_by.remove(request.user)
        else:
            project.starred_by.add(request.user)

    return redirect("main:show_projects")