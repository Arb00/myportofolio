import datetime
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.staticfiles import finders
from django.core import serializers
from django.core.cache import cache
from django.core.paginator import Paginator
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.templatetags.static import static
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from main.forms import ExperienceForm, MessageForm, ProjectForm
from main.models import Education, Experience, Project, Skill

# Jumlah kartu per halaman untuk "muat lebih banyak" di daftar Experience dan Projects
PAGE_SIZE = 6

# File CV opsional; tombol Download CV hanya muncul kalau file ini ada di static/
CV_STATIC_PATH = "files/CV_Muhammad_Sabri.pdf"

# Rate limit form Contact: maksimal 3 pesan per 10 menit untuk tiap alamat IP
CONTACT_RATE_LIMIT = 3
CONTACT_RATE_WINDOW = 600


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
        "skills": Skill.objects.all(),
        "contact_form": MessageForm(),
        "cv_url": static(CV_STATIC_PATH) if finders.find(CV_STATIC_PATH) else None,
    }
    return render(request, "index.html", context)


def _client_ip(request):
    """Di belakang reverse proxy, alamat pengunjung ada di X-Forwarded-For."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


@require_POST
def send_message_ajax(request):
    """Simpan pesan dari form Contact. Balas JSON: 201 sukses, 400 invalid, 429 terlalu sering."""
    cache_key = f"contact-rate:{_client_ip(request)}"
    sent_count = cache.get(cache_key, 0)
    if sent_count >= CONTACT_RATE_LIMIT:
        return JsonResponse(
            {"message": "Terlalu banyak pesan. Coba lagi beberapa menit lagi."},
            status=429,
        )

    form = MessageForm(request.POST)
    if form.is_valid():
        form.save()
        cache.set(cache_key, sent_count + 1, CONTACT_RATE_WINDOW)
        return JsonResponse({"message": "Pesan berhasil dikirim. Terima kasih!"}, status=201)
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


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


def _paginated_json(request, queryset, to_dict):
    """Tanpa ?page: seluruh data sebagai list (bentuk lama, tetap didukung).
    Dengan ?page=N: objek berisi results, page, dan has_next untuk "muat lebih banyak"."""
    if "page" not in request.GET:
        return JsonResponse([to_dict(obj) for obj in queryset], safe=False)

    page = Paginator(queryset, PAGE_SIZE).get_page(request.GET.get("page"))
    return JsonResponse({
        "results": [to_dict(obj) for obj in page.object_list],
        "page": page.number,
        "has_next": page.has_next(),
    })


def _redirect_back(request, fallback):
    """Kembali ke halaman asal (field next) kalau URL-nya aman, selain itu ke fallback."""
    next_url = request.POST.get("next", "")
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(next_url)
    return redirect(fallback)


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
        .order_by("-started_at", "id")
    )
    experiences, _ = _filter_by_title(request, experiences)

    # Ambil ID experience yang sudah di-star user ini dalam satu query
    starred_ids = set()
    if request.user.is_authenticated:
        starred_ids = set(
            request.user.starred_experiences.values_list("id", flat=True)
        )

    def to_dict(exp):
        return {
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

    return _paginated_json(request, experiences, to_dict)


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
    return _redirect_back(request, "main:show_experience")


# ---------- Project ----------

def get_projects_json(request):
    # Diurutkan supaya pembagian halaman konsisten (Project tidak punya tanggal dibuat)
    projects = Project.objects.prefetch_related('starred_by').order_by("title", "id")
    projects, _ = _filter_by_title(request, projects)

    def to_dict(project):
        starred_users = project.starred_by.all()
        is_starred = request.user in starred_users if request.user.is_authenticated else False
        starred_by_names = ", ".join([u.username for u in starred_users])
        return {
            "pk": str(project.id),
            "fields": {
                "title": project.title,
                "description": project.description,
                "tech_stack": project.tech_stack,
                "project_url": project.project_url,
                "project_image_url": project.project_image_url,
                "star_count": len(starred_users),
                "is_starred": is_starred,
                "starred_by_names": starred_by_names,
            }
        }

    return _paginated_json(request, projects, to_dict)


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


def show_project_detail(request, project_id):
    project = get_object_or_404(Project, pk=project_id)
    context = {
        "name": "Muhammad Sabri",
        "project": project,
        "tech_list": [tech.strip() for tech in project.tech_stack.split(",") if tech.strip()],
        "star_count": project.starred_by.count(),
        "is_starred": (
            request.user.is_authenticated
            and project.starred_by.filter(pk=request.user.pk).exists()
        ),
    }
    return render(request, "project_detail.html", context)

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
    return _redirect_back(request, "main:show_projects")

# ---------- AJAX: tambah, edit, hapus ----------
# Izin dicek di dalam view (bukan hanya menyembunyikan tombol) dan balasan selalu JSON:
# 200/201 sukses, 400 form invalid, 403 tanpa izin, 404 data tidak ditemukan.

def _json_message(message, status):
    return JsonResponse({"message": message}, status=status)


def _save_form_ajax(form, success_message, status):
    if form.is_valid():
        obj = form.save()
        return JsonResponse({"message": success_message, "pk": str(obj.id)}, status=status)
    return JsonResponse({"errors": form.errors.get_json_data()}, status=400)


@require_POST
def create_project_ajax(request):
    if not request.user.has_perm("main.add_project"):
        return _json_message("Hanya pemilik portofolio yang dapat menambahkan proyek.", 403)
    return _save_form_ajax(ProjectForm(request.POST), "Proyek berhasil ditambahkan.", 201)


@require_POST
def edit_project_ajax(request, project_id):
    if not request.user.has_perm("main.change_project"):
        return _json_message("Kamu tidak memiliki izin untuk mengubah proyek.", 403)
    project = Project.objects.filter(pk=project_id).first()
    if project is None:
        return _json_message("Proyek tidak ditemukan.", 404)
    form = ProjectForm(request.POST, instance=project)
    return _save_form_ajax(form, "Proyek berhasil diperbarui.", 200)


@require_POST
def delete_project_ajax(request, project_id):
    if not request.user.has_perm("main.delete_project"):
        return _json_message("Kamu tidak memiliki izin untuk menghapus proyek.", 403)
    project = Project.objects.filter(pk=project_id).first()
    if project is None:
        return _json_message("Proyek tidak ditemukan.", 404)
    project.delete()
    return _json_message("Proyek berhasil dihapus.", 200)


@require_POST
def create_experience_ajax(request):
    if not request.user.has_perm("main.add_experience"):
        return _json_message("Kamu tidak memiliki izin untuk menambahkan experience.", 403)
    form = ExperienceForm(request.POST)
    return _save_form_ajax(form, "Experience baru berhasil ditambahkan!", 201)


@require_POST
def edit_experience_ajax(request, experience_id):
    if not request.user.has_perm("main.change_experience"):
        return _json_message("Kamu tidak memiliki izin untuk mengubah experience.", 403)
    experience = Experience.objects.filter(pk=experience_id).first()
    if experience is None:
        return _json_message("Experience tidak ditemukan.", 404)
    form = ExperienceForm(request.POST, instance=experience)
    return _save_form_ajax(form, "Experience berhasil diperbarui!", 200)


@require_POST
def delete_experience_ajax(request, experience_id):
    if not request.user.has_perm("main.delete_experience"):
        return _json_message("Kamu tidak memiliki izin untuk menghapus experience.", 403)
    experience = Experience.objects.filter(pk=experience_id).first()
    if experience is None:
        return _json_message("Experience tidak ditemukan.", 404)
    experience.delete()
    return _json_message("Experience berhasil dihapus!", 200)
