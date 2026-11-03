import uuid
from datetime import date

from django.contrib.auth.models import Permission, User
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from main.models import Education, Experience, Message, Project, Skill
from main.views import CONTACT_RATE_LIMIT, PAGE_SIZE

PASSWORD = "Strong!Pass2468"


def create_user_with_perms(username, *codenames):
    """Buat user biasa dengan izin model app main sesuai codename yang diberikan."""
    user = User.objects.create_user(username=username, password=PASSWORD)
    perms = Permission.objects.filter(
        content_type__app_label="main", codename__in=codenames
    )
    user.user_permissions.add(*perms)
    return user


def login_url_with_next(url):
    return f"{reverse('main:login')}?next={url}"


class MainTest(TestCase):
    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )

    def test_main_url_is_accessible(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_nonexistent_page_returns_404(self):
        response = self.client.get("/halaman-yang-tidak-ada/")

        self.assertEqual(response.status_code, 404)

    def test_experience_model(self):
        self.assertEqual(str(self.experience), "Asisten Dosen PBP")
        self.assertEqual(self.experience.category, "part-time")
        self.assertTrue(self.experience.is_ongoing)

    def test_experience_page(self):
        """Halaman hanya merender kerangka; daftar diambil lewat fetch() ke endpoint JSON."""
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, reverse("main:get_experience_json"))
        self.assertNotContains(response, self.experience.title)
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:get_experience_json"))

        fields = response.json()[0]["fields"]
        self.assertFalse(self.experience.is_ongoing)
        self.assertFalse(fields["is_ongoing"])
        self.assertIsNotNone(fields["ended_at"])

    def test_experience_card_links_to_its_detail_page(self):
        """pk dari JSON dipakai JS untuk membentuk URL detail tiap kartu."""
        page = self.client.get(reverse("main:show_experience"))
        placeholder_url = reverse(
            "main:show_experience_detail",
            args=["00000000-0000-0000-0000-000000000000"],
        )
        data = self.client.get(reverse("main:get_experience_json")).json()

        self.assertContains(page, placeholder_url)
        self.assertEqual(data[0]["pk"], str(self.experience.id))

    def test_add_button_only_shown_with_permission(self):
        add_button = 'id="add-experience-button"'
        url = reverse("main:show_experience")

        self.assertNotContains(self.client.get(url), add_button)

        self.client.force_login(create_user_with_perms("editor", "add_experience"))
        self.assertContains(self.client.get(url), add_button)

    def test_experience_detail_url_is_accessible_and_uses_correct_template(self):
        detail_url = reverse("main:show_experience_detail", args=[self.experience.id])
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience_detail.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_experience_detail_returns_404_for_unknown_id(self):
        random_id = uuid.uuid4()
        response = self.client.get(
            reverse("main:show_experience_detail", args=[random_id])
        )

        self.assertEqual(response.status_code, 404)

    def test_create_experience_requires_login_and_permission(self):
        create_url = reverse("main:create_experience")

        response = self.client.get(create_url)
        self.assertRedirects(response, login_url_with_next(create_url))

        self.client.force_login(create_user_with_perms("tanpa_izin"))
        self.assertEqual(self.client.get(create_url).status_code, 403)

    def test_create_experience_page_and_valid_submission(self):
        self.client.force_login(create_user_with_perms("editor", "add_experience"))
        create_url = reverse("main:create_experience")
        response = self.client.get(create_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience_form.html")

        response = self.client.post(
            create_url,
            {
                "title": "Asisten Praktikum",
                "category": "part-time",
                "description": "Mendampingi praktikum mahasiswa.",
                "thumbnail": "",
                "ended_at": "",
            },
        )

        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertTrue(Experience.objects.filter(title="Asisten Praktikum").exists())

    def test_experience_json_and_xml_endpoints(self):
        json_response = self.client.get(reverse("main:get_experience_json"))
        xml_response = self.client.get(reverse("main:get_experience_xml"))

        self.assertEqual(json_response.status_code, 200)
        self.assertEqual(json_response["Content-Type"], "application/json")
        self.assertContains(json_response, self.experience.title)
        self.assertEqual(xml_response.status_code, 200)
        self.assertEqual(xml_response["Content-Type"], "application/xml")
        self.assertContains(xml_response, self.experience.title)

    def test_experience_json_and_xml_by_id_endpoints(self):
        json_url = reverse(
            "main:get_experience_json_by_id", args=[self.experience.id]
        )
        xml_url = reverse(
            "main:get_experience_xml_by_id", args=[self.experience.id]
        )

        json_response = self.client.get(json_url)
        xml_response = self.client.get(xml_url)

        self.assertEqual(json_response.status_code, 200)
        self.assertEqual(json_response["Content-Type"], "application/json")
        self.assertContains(json_response, self.experience.title)
        self.assertEqual(xml_response.status_code, 200)
        self.assertEqual(xml_response["Content-Type"], "application/xml")
        self.assertContains(xml_response, self.experience.title)

    def test_delete_experience_requires_login_and_permission(self):
        delete_url = reverse("main:delete_experience", args=[self.experience.id])

        response = self.client.post(delete_url)
        self.assertRedirects(response, login_url_with_next(delete_url))

        self.client.force_login(create_user_with_perms("tanpa_izin"))
        self.assertEqual(self.client.post(delete_url).status_code, 403)
        self.assertTrue(Experience.objects.filter(pk=self.experience.id).exists())

    def test_delete_experience_requires_post(self):
        self.client.force_login(create_user_with_perms("editor", "delete_experience"))
        delete_url = reverse("main:delete_experience", args=[self.experience.id])

        self.assertEqual(self.client.get(delete_url).status_code, 405)
        self.assertTrue(Experience.objects.filter(pk=self.experience.id).exists())

        response = self.client.post(delete_url)
        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertFalse(Experience.objects.filter(pk=self.experience.id).exists())


class ExperienceJsonTest(TestCase):
    """Kasus uji untuk endpoint get_experience_json (star dan filter judul)."""

    def setUp(self):
        self.url = reverse("main:get_experience_json")
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )
        self.other = Experience.objects.create(
            title="Magang Data Analyst",
            description="Mengolah data penjualan.",
            category="internship",
        )
        self.user = User.objects.create_user(username="pengunjung", password=PASSWORD)
        self.other_user = User.objects.create_user(username="lain", password=PASSWORD)

    def _fields_by_pk(self):
        return {item["pk"]: item["fields"] for item in self.client.get(self.url).json()}

    def test_fields_for_anonymous_visitor(self):
        fields = self._fields_by_pk()[str(self.experience.id)]

        self.assertEqual(fields["title"], "Asisten Dosen PBP")
        self.assertEqual(fields["category"], "part-time")
        self.assertEqual(fields["category_display"], "Part-Time")
        self.assertEqual(fields["thumbnail"], "")
        self.assertTrue(fields["is_ongoing"])
        self.assertEqual(fields["star_count"], 0)
        self.assertFalse(fields["is_starred"])

    def test_star_count_counts_all_users(self):
        self.experience.stars.add(self.user, self.other_user)
        self.other.stars.add(self.user)
        data = self._fields_by_pk()

        self.assertEqual(data[str(self.experience.id)]["star_count"], 2)
        self.assertEqual(data[str(self.other.id)]["star_count"], 1)

    def test_is_starred_follows_logged_in_user(self):
        self.experience.stars.add(self.user)

        # Anonim tidak pernah dianggap sudah memberi star
        self.assertFalse(self._fields_by_pk()[str(self.experience.id)]["is_starred"])

        self.client.force_login(self.user)
        data = self._fields_by_pk()
        self.assertTrue(data[str(self.experience.id)]["is_starred"])
        self.assertFalse(data[str(self.other.id)]["is_starred"])

        self.client.force_login(self.other_user)
        self.assertFalse(self._fields_by_pk()[str(self.experience.id)]["is_starred"])

    def test_toggle_star_updates_json(self):
        self.client.force_login(self.user)
        star_url = reverse("main:toggle_experience_star", args=[self.experience.id])

        self.client.post(star_url)
        fields = self._fields_by_pk()[str(self.experience.id)]
        self.assertEqual(fields["star_count"], 1)
        self.assertTrue(fields["is_starred"])

        self.client.post(star_url)
        fields = self._fields_by_pk()[str(self.experience.id)]
        self.assertEqual(fields["star_count"], 0)
        self.assertFalse(fields["is_starred"])

    def test_title_filter(self):
        data = self.client.get(self.url, {"title": "asisten"}).json()
        self.assertEqual([item["pk"] for item in data], [str(self.experience.id)])

        self.assertEqual(len(self.client.get(self.url, {"title": "  "}).json()), 2)
        self.assertEqual(self.client.get(self.url, {"title": "tidak ada"}).json(), [])


class CreateExperienceAjaxTest(TestCase):
    """Kasus uji untuk create_experience_ajax: 201/400/403 dan strip_tags."""

    def setUp(self):
        self.url = reverse("main:create_experience_ajax")
        self.editor = create_user_with_perms("editor", "add_experience")
        self.data = {
            "title": "Asisten Praktikum",
            "category": "part-time",
            "description": "Mendampingi praktikum mahasiswa.",
            "thumbnail": "",
            "ended_at": "",
        }

    def test_get_is_not_allowed(self):
        self.client.force_login(self.editor)

        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_anonymous_gets_403(self):
        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 403)
        self.assertIn("message", response.json())
        self.assertFalse(Experience.objects.exists())

    def test_user_without_permission_gets_403(self):
        self.client.force_login(create_user_with_perms("tanpa_izin"))
        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Experience.objects.exists())

    def test_valid_submission_returns_201(self):
        self.client.force_login(self.editor)
        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 201)
        experience = Experience.objects.get(title="Asisten Praktikum")
        self.assertEqual(response.json()["pk"], str(experience.id))

    def test_invalid_submission_returns_400_with_field_errors(self):
        self.client.force_login(self.editor)
        response = self.client.post(self.url, {**self.data, "title": ""})

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json()["errors"])
        self.assertFalse(Experience.objects.exists())

    def test_html_tags_are_stripped(self):
        self.client.force_login(self.editor)
        response = self.client.post(
            self.url,
            {
                **self.data,
                "title": "<b>Asisten</b> Riset",
                "description": "<script>alert(1)</script>Membantu riset.",
            },
        )

        self.assertEqual(response.status_code, 201)
        experience = Experience.objects.get()
        self.assertEqual(experience.title, "Asisten Riset")
        self.assertNotIn("<", experience.description)
        self.assertIn("Membantu riset.", experience.description)

    def test_title_with_only_tags_returns_400(self):
        self.client.force_login(self.editor)
        response = self.client.post(self.url, {**self.data, "title": "<b></b>"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json()["errors"])
        self.assertFalse(Experience.objects.exists())


class EducationTest(TestCase):
    """Kasus uji untuk fitur Education (Individual Assignment 2)."""

    def setUp(self):
        self.education = Education.objects.create(
            institution="Universitas Indonesia",
            level="S1",
            field_of_study="Ilmu Komputer",
            description="Berfokus pada sains data dan kecerdasan buatan.",
            started_at=date(2024, 8, 1),
        )

    def test_education_url_is_accessible_and_uses_correct_template(self):
        """URL /education/ dapat diakses dan menggunakan template education.html."""
        response = self.client.get(reverse("main:show_education"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "education.html")
        # navbar & footer tetap konsisten dengan halaman lain
        self.assertContains(response, f'href="{reverse("main:show_main")}"')
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_education_page_shows_data_when_available(self):
        """Data model Education muncul di halaman HTML ketika data ada."""
        response = self.client.get(reverse("main:show_education"))

        self.assertContains(response, self.education.institution)
        self.assertContains(response, self.education.field_of_study)
        self.assertContains(response, self.education.description)
        self.assertContains(response, "Sarjana")  # get_level_display()
        self.assertContains(response, "Sedang berlangsung")

    def test_empty_education_page_shows_empty_state(self):
        """Halaman menampilkan pesan kondisi kosong ketika belum ada data."""
        Education.objects.all().delete()
        response = self.client.get(reverse("main:show_education"))

        self.assertContains(response, "Belum ada pendidikan yang ditambahkan.")

    def test_completed_education(self):
        self.education.ended_at = date(2028, 6, 30)
        self.education.save()
        response = self.client.get(reverse("main:show_education"))

        self.assertContains(response, "Selesai")

    def test_institution_name_links_to_website_when_set(self):
        """Nama institusi jadi tautan ke situs sekolah kalau field website diisi."""
        self.education.website = "https://www.ui.ac.id"
        self.education.save()
        response = self.client.get(reverse("main:show_education"))

        self.assertContains(response, f'href="{self.education.website}"')
        self.assertContains(response, 'class="education-link"')

    def test_institution_name_is_plain_text_when_website_is_empty(self):
        """Kalau website kosong, nama institusi tetap tampil tanpa tautan."""
        response = self.client.get(reverse("main:show_education"))

        self.assertNotContains(response, "education-link")


class ProjectTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="Fern AI Assistant",
            description="Build personal AI Assistant with Hermes and Gemini API.",
            tech_stack="AWS, Gemini API, Hermes, Discord Bot",
            project_url="https://github.com/example/fern-ai",
            project_image_url="https://example.com/image.png",
        )

    def test_project_str(self):
        self.assertEqual(str(self.project), "Fern AI Assistant")

    def test_show_projects_view(self):
        """Halaman hanya merender kerangka; daftar diambil lewat fetch() ke API DRF."""
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project.html")
        self.assertContains(response, reverse("api:project-list"))
        self.assertNotContains(response, self.project.title)

    def test_show_projects_filter(self):
        url = reverse("main:get_projects_json")

        data = self.client.get(url, {"title": "fern"}).json()
        self.assertEqual([item["pk"] for item in data], [str(self.project.id)])

        self.assertEqual(self.client.get(url, {"title": "NonExistent"}).json(), [])

        # Kata kunci dari query string diisikan kembali ke kolom pencarian
        page = self.client.get(reverse("main:show_projects"), {"title": "Fern"})
        self.assertContains(page, 'value="Fern"')

    def test_empty_projects(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Belum ada proyek yang ditambahkan atau ditemukan.")
        self.assertEqual(self.client.get(reverse("main:get_projects_json")).json(), [])

    def test_add_button_only_shown_to_owner(self):
        """Sejak Tutorial 07, Projects hanya dikelola pemilik (superuser), sama dengan API."""
        add_button = 'id="add-project-button"'
        url = reverse("main:show_projects")

        self.assertNotContains(self.client.get(url), add_button)

        self.client.force_login(create_user_with_perms("editor", "add_project"))
        self.assertNotContains(self.client.get(url), add_button)

        self.client.force_login(User.objects.create_superuser("owner", password=PASSWORD))
        self.assertContains(self.client.get(url), add_button)

    def test_create_project_requires_login_and_permission(self):
        create_url = reverse("main:create_project")

        response = self.client.get(create_url)
        self.assertRedirects(response, login_url_with_next(create_url))

        self.client.force_login(create_user_with_perms("tanpa_izin"))
        self.assertEqual(self.client.get(create_url).status_code, 403)

    def test_create_project_view_get(self):
        self.client.force_login(create_user_with_perms("editor", "add_project"))
        response = self.client.get(reverse("main:create_project"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects_form.html")

    def test_create_project_view_post_valid(self):
        self.client.force_login(create_user_with_perms("editor", "add_project"))
        data = {
            "title": "New Web Project",
            "description": "A very cool new web project",
            "tech_stack": "Django, HTML, CSS",
            "project_url": "https://github.com/example/web-project",
            "project_image_url": "https://example.com/img.png",
        }
        response = self.client.post(reverse("main:create_project"), data=data)
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertTrue(Project.objects.filter(title="New Web Project").exists())

    def test_delete_project_requires_login_and_permission(self):
        delete_url = reverse("main:delete_project", kwargs={"project_id": self.project.id})

        response = self.client.post(delete_url)
        self.assertRedirects(response, login_url_with_next(delete_url))

        self.client.force_login(create_user_with_perms("tanpa_izin"))
        self.assertEqual(self.client.post(delete_url).status_code, 403)
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

    def test_delete_project(self):
        self.client.force_login(create_user_with_perms("editor", "delete_project"))
        delete_url = reverse("main:delete_project", kwargs={"project_id": self.project.id})

        self.assertEqual(self.client.get(delete_url).status_code, 405)
        self.assertTrue(Project.objects.filter(id=self.project.id).exists())

        response = self.client.post(delete_url)
        self.assertRedirects(response, reverse("main:show_projects"))
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_get_projects_json(self):
        response = self.client.get(reverse("main:get_projects_json"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertContains(response, "Fern AI Assistant")

    def test_get_projects_json_star_fields(self):
        user = User.objects.create_user(username="pengunjung", password=PASSWORD)
        self.project.starred_by.add(user)
        url = reverse("main:get_projects_json")

        fields = self.client.get(url).json()[0]["fields"]
        self.assertEqual(fields["star_count"], 1)
        self.assertFalse(fields["is_starred"])
        self.assertEqual(fields["starred_by_names"], "pengunjung")

        self.client.force_login(user)
        self.assertTrue(self.client.get(url).json()[0]["fields"]["is_starred"])

    def test_get_project_json_by_id(self):
        response = self.client.get(reverse("main:get_project_json_by_id", kwargs={"project_id": self.project.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertContains(response, "Fern AI Assistant")

    def test_get_projects_xml(self):
        response = self.client.get(reverse("main:get_projects_xml"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")
        self.assertContains(response, "Fern AI Assistant")

    def test_get_project_xml_by_id(self):
        response = self.client.get(reverse("main:get_project_xml_by_id", kwargs={"project_id": self.project.id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/xml")
        self.assertContains(response, "Fern AI Assistant")


class CreateProjectAjaxTest(TestCase):
    """Kasus uji untuk create_project_ajax: butuh izin main.add_project."""

    def setUp(self):
        self.url = reverse("main:create_project_ajax")
        self.owner = User.objects.create_superuser("pemilik", password=PASSWORD)
        self.data = {
            "title": "New Web Project",
            "description": "A very cool new web project",
            "tech_stack": "Django, HTML, CSS",
            "project_url": "https://github.com/example/web-project",
            "project_image_url": "https://example.com/img.png",
        }

    def test_get_is_not_allowed(self):
        self.client.force_login(self.owner)

        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_anonymous_gets_403(self):
        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 403)
        self.assertIn("message", response.json())
        self.assertFalse(Project.objects.exists())

    def test_regular_user_gets_403(self):
        self.client.force_login(User.objects.create_user("pengunjung", password=PASSWORD))
        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 403)
        self.assertFalse(Project.objects.exists())

    def test_user_with_add_permission_returns_201(self):
        self.client.force_login(create_user_with_perms("editor", "add_project"))
        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(Project.objects.filter(title="New Web Project").exists())

    def test_valid_submission_returns_201(self):
        self.client.force_login(self.owner)
        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 201)
        project = Project.objects.get(title="New Web Project")
        self.assertEqual(response.json()["pk"], str(project.id))

    def test_invalid_submission_returns_400_with_field_errors(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            self.url, {**self.data, "title": "", "project_url": "bukan-url"}
        )

        self.assertEqual(response.status_code, 400)
        errors = response.json()["errors"]
        self.assertIn("title", errors)
        self.assertIn("project_url", errors)
        self.assertFalse(Project.objects.exists())

    def test_html_tags_are_stripped(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            self.url,
            {
                **self.data,
                "title": "<i>Portofolio</i> Web",
                "tech_stack": "<b>Django</b>, CSS",
                "description": "<script>alert(1)</script>Situs pribadi.",
            },
        )

        self.assertEqual(response.status_code, 201)
        project = Project.objects.get()
        self.assertEqual(project.title, "Portofolio Web")
        self.assertEqual(project.tech_stack, "Django, CSS")
        self.assertNotIn("<", project.description)
        self.assertIn("Situs pribadi.", project.description)


class EditDeleteExperienceAjaxTest(TestCase):
    """Kasus uji edit dan hapus experience lewat AJAX: 200/400/403/404."""

    def setUp(self):
        self.experience = Experience.objects.create(
            title="Asisten Dosen PBP",
            description="Membantu mahasiswa memahami pengembangan web.",
            category="part-time",
        )
        self.edit_url = reverse("main:edit_experience_ajax", args=[self.experience.id])
        self.delete_url = reverse("main:delete_experience_ajax", args=[self.experience.id])
        self.editor = create_user_with_perms(
            "editor", "change_experience", "delete_experience"
        )
        self.data = {
            "title": "Asisten Dosen PBP Diperbarui",
            "category": "research",
            "description": "Deskripsi baru.",
            "thumbnail": "",
            "ended_at": "2026-10-01T09:30",
        }

    def test_edit_and_delete_reject_get(self):
        self.client.force_login(self.editor)

        self.assertEqual(self.client.get(self.edit_url).status_code, 405)
        self.assertEqual(self.client.get(self.delete_url).status_code, 405)

    def test_edit_without_permission_returns_403(self):
        for user in (None, create_user_with_perms("tanpa_izin")):
            if user:
                self.client.force_login(user)
            response = self.client.post(self.edit_url, self.data)

            self.assertEqual(response.status_code, 403)
            self.assertIn("message", response.json())
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Asisten Dosen PBP")

    def test_edit_valid_returns_200_and_updates(self):
        self.client.force_login(self.editor)
        response = self.client.post(self.edit_url, self.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["pk"], str(self.experience.id))
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Asisten Dosen PBP Diperbarui")
        self.assertEqual(self.experience.category, "research")
        self.assertFalse(self.experience.is_ongoing)
        self.assertEqual(Experience.objects.count(), 1)

    def test_edit_invalid_returns_400_and_keeps_data(self):
        self.client.force_login(self.editor)
        response = self.client.post(self.edit_url, {**self.data, "title": "<b></b>"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json()["errors"])
        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Asisten Dosen PBP")

    def test_edit_strips_html_tags(self):
        self.client.force_login(self.editor)
        self.client.post(self.edit_url, {**self.data, "title": "<i>Asisten</i> Riset"})

        self.experience.refresh_from_db()
        self.assertEqual(self.experience.title, "Asisten Riset")

    def test_edit_and_delete_unknown_id_return_404_json(self):
        self.client.force_login(self.editor)
        unknown_id = uuid.uuid4()

        for name in ("main:edit_experience_ajax", "main:delete_experience_ajax"):
            response = self.client.post(reverse(name, args=[unknown_id]), self.data)

            self.assertEqual(response.status_code, 404)
            self.assertEqual(response["Content-Type"], "application/json")
            self.assertIn("message", response.json())

    def test_unknown_id_without_permission_returns_403_not_404(self):
        """Izin dicek lebih dulu supaya keberadaan data tidak bocor ke yang tidak berhak."""
        response = self.client.post(
            reverse("main:delete_experience_ajax", args=[uuid.uuid4()])
        )

        self.assertEqual(response.status_code, 403)

    def test_delete_without_permission_returns_403(self):
        for user in (None, create_user_with_perms("tanpa_izin", "change_experience")):
            if user:
                self.client.force_login(user)

            self.assertEqual(self.client.post(self.delete_url).status_code, 403)
        self.assertTrue(Experience.objects.filter(pk=self.experience.id).exists())

    def test_delete_returns_200_and_removes(self):
        self.client.force_login(self.editor)
        response = self.client.post(self.delete_url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
        self.assertFalse(Experience.objects.filter(pk=self.experience.id).exists())


class EditDeleteProjectAjaxTest(TestCase):
    """Kasus uji edit dan hapus proyek lewat AJAX: 200/400/403/404."""

    def setUp(self):
        self.project = Project.objects.create(
            title="Fern AI Assistant",
            description="Build personal AI Assistant with Hermes and Gemini API.",
            tech_stack="AWS, Gemini API",
        )
        self.edit_url = reverse("main:edit_project_ajax", args=[self.project.id])
        self.delete_url = reverse("main:delete_project_ajax", args=[self.project.id])
        self.editor = create_user_with_perms("editor", "change_project", "delete_project")
        self.data = {
            "title": "Fern AI Assistant Updated",
            "description": "Updated description here.",
            "tech_stack": "Django, Gemini API",
            "project_url": "https://github.com/example/updated",
            "project_image_url": "",
        }

    def test_edit_and_delete_reject_get(self):
        self.client.force_login(self.editor)

        self.assertEqual(self.client.get(self.edit_url).status_code, 405)
        self.assertEqual(self.client.get(self.delete_url).status_code, 405)

    def test_edit_without_permission_returns_403(self):
        for user in (None, create_user_with_perms("tanpa_izin", "add_project")):
            if user:
                self.client.force_login(user)

            self.assertEqual(self.client.post(self.edit_url, self.data).status_code, 403)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Fern AI Assistant")

    def test_edit_valid_returns_200_and_updates(self):
        self.client.force_login(self.editor)
        response = self.client.post(self.edit_url, self.data)

        self.assertEqual(response.status_code, 200)
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Fern AI Assistant Updated")
        self.assertEqual(self.project.project_url, "https://github.com/example/updated")
        self.assertEqual(Project.objects.count(), 1)

    def test_edit_invalid_returns_400_and_keeps_data(self):
        self.client.force_login(self.editor)
        response = self.client.post(self.edit_url, {**self.data, "project_url": "bukan-url"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("project_url", response.json()["errors"])
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, "Fern AI Assistant")

    def test_edit_and_delete_unknown_id_return_404_json(self):
        self.client.force_login(self.editor)
        unknown_id = uuid.uuid4()

        for name in ("main:edit_project_ajax", "main:delete_project_ajax"):
            response = self.client.post(reverse(name, args=[unknown_id]), self.data)

            self.assertEqual(response.status_code, 404)
            self.assertEqual(response["Content-Type"], "application/json")

    def test_delete_without_permission_returns_403(self):
        for user in (None, create_user_with_perms("tanpa_izin", "change_project")):
            if user:
                self.client.force_login(user)

            self.assertEqual(self.client.post(self.delete_url).status_code, 403)
        self.assertTrue(Project.objects.filter(pk=self.project.id).exists())

    def test_delete_returns_200_and_removes(self):
        self.client.force_login(self.editor)
        response = self.client.post(self.delete_url)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Project.objects.filter(pk=self.project.id).exists())


class PaginationTest(TestCase):
    """Kasus uji "muat lebih banyak": JSON berisi results, page, dan has_next."""

    def setUp(self):
        self.total = PAGE_SIZE + 2
        for number in range(self.total):
            Experience.objects.create(
                title=f"Experience {number:02d}", description="Deskripsi.", category="part-time"
            )
            Project.objects.create(
                title=f"Project {number:02d}", description="Deskripsi.", tech_stack="Django"
            )
        self.urls = [reverse("main:get_experience_json"), reverse("main:get_projects_json")]

    def test_without_page_returns_full_list(self):
        for url in self.urls:
            data = self.client.get(url).json()

            self.assertIsInstance(data, list)
            self.assertEqual(len(data), self.total)

    def test_pages_cover_all_items_without_duplicates(self):
        for url in self.urls:
            first = self.client.get(url, {"page": 1}).json()
            second = self.client.get(url, {"page": 2}).json()

            self.assertEqual(first["page"], 1)
            self.assertTrue(first["has_next"])
            self.assertEqual(len(first["results"]), PAGE_SIZE)
            self.assertEqual(second["page"], 2)
            self.assertFalse(second["has_next"])
            self.assertEqual(len(second["results"]), 2)

            pks = [item["pk"] for item in first["results"] + second["results"]]
            self.assertEqual(len(set(pks)), self.total)

    def test_invalid_page_falls_back_safely(self):
        for url in self.urls:
            self.assertEqual(self.client.get(url, {"page": "abc"}).json()["page"], 1)
            self.assertEqual(self.client.get(url, {"page": 99}).json()["page"], 2)

    def test_page_works_with_title_filter(self):
        for url in self.urls:
            data = self.client.get(url, {"page": 1, "title": "00"}).json()

            self.assertEqual(len(data["results"]), 1)
            self.assertFalse(data["has_next"])


class ProjectDetailTest(TestCase):
    def setUp(self):
        self.project = Project.objects.create(
            title="Fern AI Assistant",
            description="Build personal AI Assistant.",
            tech_stack="AWS, Gemini API , Hermes",
            project_url="https://github.com/example/fern-ai",
            project_image_url="https://example.com/image.png",
        )
        self.url = reverse("main:show_project_detail", args=[self.project.id])
        self.user = User.objects.create_user(username="pengunjung", password=PASSWORD)

    def test_detail_page_shows_project(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project_detail.html")
        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.description)
        self.assertContains(response, f'href="{self.project.project_url}"')
        self.assertContains(response, f'src="{self.project.project_image_url}"')
        self.assertContains(response, f'href="{reverse("main:show_projects")}"')

    def test_detail_page_uses_article_and_aside(self):
        response = self.client.get(self.url)

        self.assertContains(response, "<article")
        self.assertContains(response, "<aside")

    def test_tech_stack_is_split_into_list(self):
        response = self.client.get(self.url)

        self.assertEqual(response.context["tech_list"], ["AWS", "Gemini API", "Hermes"])
        self.assertContains(response, "<li>Gemini API</li>")

    def test_unknown_id_returns_404(self):
        response = self.client.get(reverse("main:show_project_detail", args=[uuid.uuid4()]))

        self.assertEqual(response.status_code, 404)

    def test_description_is_escaped(self):
        self.project.description = "<script>alert(1)</script>"
        self.project.save()
        response = self.client.get(self.url)

        self.assertNotContains(response, "<script>alert(1)</script>")

    def test_star_button_for_anonymous_links_to_login(self):
        response = self.client.get(self.url)

        self.assertFalse(response.context["is_starred"])
        self.assertNotContains(response, reverse("main:toggle_star", args=[self.project.id]))

    def test_star_from_detail_returns_to_detail(self):
        self.client.force_login(self.user)
        star_url = reverse("main:toggle_star", args=[self.project.id])

        response = self.client.post(star_url, {"next": self.url})
        self.assertRedirects(response, self.url)

        detail = self.client.get(self.url)
        self.assertTrue(detail.context["is_starred"])
        self.assertEqual(detail.context["star_count"], 1)

    def test_star_ignores_unsafe_next(self):
        self.client.force_login(self.user)
        star_url = reverse("main:toggle_star", args=[self.project.id])

        response = self.client.post(star_url, {"next": "https://evil.example.com/"})
        self.assertRedirects(response, reverse("main:show_projects"))


class SkillTest(TestCase):
    def test_skills_section_hidden_when_empty(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertNotContains(response, 'id="skills"')

    def test_skills_grouped_by_category_on_home(self):
        Skill.objects.create(name="Python", category="language", level=3)
        Skill.objects.create(name="Django", category="framework", level=2)
        response = self.client.get(reverse("main:show_main"))

        self.assertContains(response, 'id="skills"')
        self.assertContains(response, "Python")
        self.assertContains(response, "Bahasa Pemrograman")
        self.assertContains(response, "Mahir")
        self.assertContains(response, "Django")
        self.assertContains(response, "Framework &amp; Library")
        self.assertContains(response, "Menengah")

    def test_skill_str(self):
        self.assertEqual(str(Skill(name="Python")), "Python")


class ContactTest(TestCase):
    """Kasus uji form Contact: 201/400/429, strip_tags, dan penyimpanan Message."""

    def setUp(self):
        # Hitungan rate limit disimpan di cache, jadi dikosongkan di tiap test
        cache.clear()
        self.addCleanup(cache.clear)
        self.url = reverse("main:send_message_ajax")
        self.data = {
            "name": "Budi",
            "email": "budi@example.com",
            "message": "Halo, saya tertarik berkolaborasi.",
        }

    def test_home_shows_contact_form(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertContains(response, 'id="contact-form"')
        self.assertContains(response, f'action="{self.url}"')
        for field in ("name", "email", "message"):
            self.assertContains(response, f'<label for="id_{field}">')

    def test_get_is_not_allowed(self):
        self.assertEqual(self.client.get(self.url).status_code, 405)

    def test_valid_message_is_saved(self):
        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 201)
        self.assertIn("message", response.json())
        message = Message.objects.get()
        self.assertEqual(message.name, "Budi")
        self.assertEqual(message.email, "budi@example.com")
        self.assertEqual(str(message), "Budi <budi@example.com>")

    def test_invalid_message_returns_400_with_field_errors(self):
        response = self.client.post(
            self.url, {"name": "", "email": "bukan-email", "message": ""}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(set(response.json()["errors"]), {"name", "email", "message"})
        self.assertFalse(Message.objects.exists())

    def test_too_long_message_returns_400(self):
        response = self.client.post(self.url, {**self.data, "message": "a" * 2001})

        self.assertEqual(response.status_code, 400)
        self.assertIn("message", response.json()["errors"])

    def test_html_tags_are_stripped(self):
        response = self.client.post(
            self.url,
            {
                **self.data,
                "name": "<b>Budi</b>",
                "message": "<script>alert(1)</script>Halo <i>Sabri</i>",
            },
        )

        self.assertEqual(response.status_code, 201)
        message = Message.objects.get()
        self.assertEqual(message.name, "Budi")
        self.assertNotIn("<", message.message)
        self.assertIn("Halo Sabri", message.message)

    def test_message_with_only_tags_returns_400(self):
        response = self.client.post(self.url, {**self.data, "message": "<p></p>"})

        self.assertEqual(response.status_code, 400)
        self.assertIn("message", response.json()["errors"])

    def test_rate_limit_returns_429(self):
        for _ in range(CONTACT_RATE_LIMIT):
            self.assertEqual(self.client.post(self.url, self.data).status_code, 201)

        response = self.client.post(self.url, self.data)

        self.assertEqual(response.status_code, 429)
        self.assertIn("message", response.json())
        self.assertEqual(Message.objects.count(), CONTACT_RATE_LIMIT)

    def test_invalid_messages_do_not_use_up_rate_limit(self):
        for _ in range(CONTACT_RATE_LIMIT + 1):
            self.client.post(self.url, {**self.data, "email": "bukan-email"})

        self.assertEqual(self.client.post(self.url, self.data).status_code, 201)

    def test_rate_limit_is_per_ip(self):
        for _ in range(CONTACT_RATE_LIMIT):
            self.client.post(self.url, self.data, REMOTE_ADDR="10.0.0.1")

        blocked = self.client.post(self.url, self.data, REMOTE_ADDR="10.0.0.1")
        other = self.client.post(self.url, self.data, REMOTE_ADDR="10.0.0.2")

        self.assertEqual(blocked.status_code, 429)
        self.assertEqual(other.status_code, 201)


class SiteChromeTest(TestCase):
    """Kasus uji elemen bersama di base.html: meta SEO, favicon, tema, footer."""

    def setUp(self):
        self.response = self.client.get(reverse("main:show_main"))

    def test_meta_description_and_open_graph(self):
        self.assertContains(self.response, '<meta name="description" content="')
        self.assertContains(self.response, '<meta property="og:title" content="Muhammad Sabri - Portofolio">')
        self.assertContains(self.response, '<meta property="og:url" content="http://testserver/">')
        self.assertContains(self.response, 'property="og:image" content="http://testserver/static/img/')

    def test_favicon_and_theme_toggle(self):
        self.assertContains(self.response, 'rel="icon"')
        self.assertContains(self.response, 'id="theme-toggle"')
        self.assertContains(self.response, "prefers-color-scheme")

    def test_footer_links(self):
        self.assertContains(self.response, "https://www.linkedin.com/in/muhammadsabri67/")
        self.assertContains(self.response, "https://github.com/Arb00/")

    def test_cv_button_hidden_until_file_exists(self):
        self.assertIsNone(self.response.context["cv_url"])
        self.assertNotContains(self.response, "Download CV")

    def test_project_detail_overrides_og_title(self):
        project = Project.objects.create(
            title="Fern AI Assistant", description="Deskripsi.", tech_stack="Django"
        )
        response = self.client.get(reverse("main:show_project_detail", args=[project.id]))

        self.assertContains(
            response, '<meta property="og:title" content="Fern AI Assistant - Muhammad Sabri">'
        )


class LastLoginCookieTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="cookie_user",
            password="Strong!Pass2468",
        )

    def test_login_sets_cookie_and_profile_displays_it(self):
        response = self.client.post(
            reverse("main:login"),
            {"username": "cookie_user", "password": "Strong!Pass2468"},
        )

        self.assertRedirects(response, reverse("main:show_main"))
        last_login = response.cookies["last_login"].value
        self.assertRegex(last_login, r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$")

        profile = self.client.get(reverse("main:show_main"))
        self.assertContains(profile, "Sesi Terakhir Login")
        self.assertContains(profile, last_login)

    def test_profile_uses_fallback_when_cookie_is_missing(self):
        response = self.client.get(reverse("main:show_main"))

        self.assertContains(response, "Belum ada sesi login / Cookie tidak ditemukan")

    def test_logout_deletes_last_login_cookie(self):
        self.client.force_login(self.user)
        self.client.cookies["last_login"] = "2026-09-28 10:00:00"

        response = self.client.get(reverse("main:logout"))

        self.assertRedirects(response, reverse("main:show_main"))
        self.assertEqual(response.cookies["last_login"].value, "")
