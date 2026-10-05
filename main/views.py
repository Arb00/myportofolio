import datetime
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core import serializers
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from main.forms import ExperienceForm, ProjectForm
from main.models import Education, Experience, Project


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
        response.set_cookie(
            "last_login",
            datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        return response

    context = {
        "name": "Muhammad Sabri",
        "form": form,
    }
    return render(request, "login.html", context)


def logout_user(request):
    logout(request)
    response = redirect("main:show_main")
    response.delete_cookie("last_login")
    return response


def show_main(request):
    last_login = request.COOKIES.get(
        "last_login",
        "Belum ada sesi login / Cookie tidak ditemukan",
    )
    context = {
        "name": "Muhammad Sabri",
        "npm": "2506623793",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Mahasiswa Ilmu Komputer Universitas Indonesia yang tertarik "
            "pada pengembangan perangkat lunak dan pendidikan."
        ),
        "last_login": last_login,
    }
    return render(request, "index.html", context)


def show_education(request):
    context = {
        "name": "Muhammad Sabri",
        "education_list": Education.objects.all(),
    }
    return render(request, "education.html", context)


# ---------- Helper ----------

def perm_required(perm):
    """Anonim -> redirect ke login; sudah login tapi tanpa izin -> HTTP 403.
    Superuser otomatis lolos karena punya semua permission."""
    def decorator(view):
        return login_required(permission_required(perm, raise_exception=True)(view))
    return decorator


def _public_fields(model):
    """Hanya field konkret. M2M starred_by (daftar ID user) sengaja tidak ikut."""
    return [f.name for f in model._meta.concrete_fields]


def _filter_by_title(request, queryset):
    query = request.GET.get("title", "").strip()
    if query:
        queryset = queryset.filter(title__icontains=query)
    return queryset, query


def _serialize(fmt, queryset, model):
    content_type = "application/json" if fmt == "json" else "application/xml"
    data = serializers.serialize(fmt, queryset, fields=_public_fields(model))
    return HttpResponse(data, content_type=content_type)


def _star_relation(obj):
    """Dukung nama relasi star lama dan baru untuk kompatibilitas model."""
    if hasattr(obj, "starred_by"):
        return obj.starred_by
    if hasattr(obj, "stars"):
        return obj.stars
    return None


def _toggle_star(user, obj):
    """Beri star jika belum, batalkan jika sudah (maksimal 1 per user)."""
    relation = _star_relation(obj)
    if relation is None:
        return
    if relation.filter(pk=user.pk).exists():
        relation.remove(user)
    else:
        relation.add(user)


# ---------- Experience ----------

def get_experience_json(request):
    """Data experience untuk AJAX, disusun manual dengan info star dari Tugas 4."""
    experiences = (
        Experience.objects
        .annotate(star_count=Count("stars", distinct=True))
        .order_by("-started_at")
    )
    experiences, _ = _filter_by_title(request, experiences)
 
    # Ambil ID experience yang sudah di-star user ini dalam satu query
    starred_ids = set()
    if request.user.is_authenticated:
        starred_ids = set(
            request.user.starred_experiences.values_list("id", flat=True)
        )
 
    data = [
        {
            "pk": str(exp.id),
            "fields": {
                "title": exp.title,
                "description": exp.description,
                "category": exp.category,
                "category_display": exp.get_category_display(),
                "thumbnail": exp.thumbnail or "",
                "started_at": exp.started_at.isoformat() if exp.started_at else None,
                "ended_at": exp.ended_at.isoformat() if exp.ended_at else None,
                "is_ongoing": exp.is_ongoing,
                "star_count": exp.star_count,
                "is_starred": exp.id in starred_ids,
            },
        }
        for exp in experiences
    ]
    return JsonResponse(data, safe=False)

def get_experience_xml(request):
    qs, _ = _filter_by_title(request, Experience.objects.all())
    return _serialize("xml", qs, Experience)


def get_experience_json_by_id(request, experience_id):
    exp = get_object_or_404(Experience, pk=experience_id)
    return _serialize("json", [exp], Experience)


def get_experience_xml_by_id(request, experience_id):
    exp = get_object_or_404(Experience, pk=experience_id)
    return _serialize("xml", [exp], Experience)


def show_experience(request):
    """Hanya merender kerangka halaman; daftar diambil lewat fetch()."""
    context = {
        "name": "Muhammad Sabri",
        "title_query": request.GET.get("title", "").strip(),
        "form": ExperienceForm(),
    }
    return render(request, "experience.html", context)


def show_experience_detail(request, id):
    context = {
        "name": "Muhammad Sabri",
        "experience": get_object_or_404(Experience, id=id),
    }
    return render(request, "experience_detail.html", context)


@perm_required("main.add_experience")
def create_experience(request):
    form = ExperienceForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman baru berhasil ditambahkan!")
        return redirect("main:show_experience")
    return render(request, "experience_form.html", {"name": "Muhammad Sabri", "form": form})


@perm_required("main.change_experience")
def edit_experience(request, experience_id):
    experience = get_object_or_404(Experience, pk=experience_id)
    form = ExperienceForm(request.POST or None, instance=experience)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Pengalaman berhasil diperbarui!")
        return redirect("main:show_experience")
    return render(request, "experience_form.html", {"name": "Muhammad Sabri", "form": form})


@perm_required("main.delete_experience")
@require_POST
def delete_experience(request, experience_id):
    get_object_or_404(Experience, pk=experience_id).delete()
    messages.success(request, "Pengalaman berhasil dihapus!")
    return redirect("main:show_experience")


@login_required
@require_POST
def toggle_experience_star(request, experience_id):
    _toggle_star(request.user, get_object_or_404(Experience, pk=experience_id))
    return redirect("main:show_experience")


# ---------- Project ----------

def get_projects_json(request):
    title_query = request.GET.get("title", "").strip()
    projects = Project.objects.prefetch_related('starred_by').all()
    if title_query:
        projects = projects.filter(title__icontains=title_query)

    data = []
    for project in projects:
        starred_users = project.starred_by.all()
        is_starred = request.user in starred_users if request.user.is_authenticated else False
        starred_by_names = ", ".join([u.username for u in starred_users])
        data.append({
            "pk": str(project.id),
            "fields": {
                "title": project.title,
                "description": project.description,
                "tech_stack": project.tech_stack,
                "project_url": project.project_url,
                "project_image_url": project.project_image_url,
                "star_count": starred_users.count(),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
            }
        })
    return JsonResponse(data, safe=False)

def get_projects_xml(request):
    qs, _ = _filter_by_title(request, Project.objects.all())
    return _serialize("xml", qs, Project)


def get_project_json_by_id(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return _serialize("json", [project], Project)


def get_project_xml_by_id(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    return _serialize("xml", [project], Project)


def show_projects(request):
    title_query = request.GET.get("title", "").strip()
    context = {
        "name": "Sabri", # Sesuaikan dengan namamu
        "title_query": title_query,
        "form": ProjectForm(),
    }
    return render(request, "project.html", context)

@perm_required("main.add_project")
def create_project(request):
    form = ProjectForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek baru berhasil ditambahkan!")
        return redirect("main:show_projects")
    return render(request, "projects_form.html", {"name": "Muhammad Sabri", "form": form})


@perm_required("main.change_project")
def edit_project(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    form = ProjectForm(request.POST or None, instance=project)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Proyek berhasil diperbarui!")
        return redirect("main:show_projects")
    context = {"name": "Muhammad Sabri", "form": form, "project": project}
    return render(request, "projects_edit.html", context)


@perm_required("main.delete_project")
@require_POST
def delete_project(request, project_id):
    get_object_or_404(Project, pk=project_id).delete()
    messages.success(request, "Project berhasil dihapus!")
    return redirect("main:show_projects")


@login_required
@require_POST
def toggle_star(request, project_id):
    _toggle_star(request.user, get_object_or_404(Project, pk=project_id))
    return redirect("main:show_projects")

@require_POST
def create_project_ajax(request):
    if not request.user.is_superuser:
        return JsonResponse({"message": "Hanya pemilik portofolio yang dapat menambahkan proyek."}, status=403)

    form = ProjectForm(request.POST)
    if form.is_valid():
        project = form.save()
        return JsonResponse({"message": "Proyek berhasil ditambahkan.", "pk": str(project.id)}, status=201)

    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)

@require_POST
def create_experience_ajax(request):
    """Tambah experience lewat AJAX. Balas JSON: 201 sukses, 400 invalid, 403 tanpa izin.
    Izin dicek di sini (bukan hanya menyembunyikan tombol) sesuai peran dari Tugas 4."""
    if not request.user.has_perm("main.add_experience"):
        return JsonResponse(
            {"message": "Kamu tidak memiliki izin untuk menambahkan experience."},
            status=403,
        )
 
    form = ExperienceForm(request.POST)
    if form.is_valid():
        experience = form.save()
        return JsonResponse(
            {"message": "Experience baru berhasil ditambahkan!", "pk": str(experience.id)},
            status=201,
        )
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)