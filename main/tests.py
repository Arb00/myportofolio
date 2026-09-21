from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import date

from main.models import Education, Experience, Project


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
        response = self.client.get(reverse("main:show_experience"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, "Part-Time")
        self.assertContains(response, "Sedang berlangsung")
        self.assertContains(response, f'href="{reverse("main:show_main")}"')

    def test_empty_experience_page(self):
        Experience.objects.all().delete()
        response = self.client.get(reverse("main:show_experience"))

        self.assertContains(response, "Belum ada pengalaman yang ditambahkan.")

    def test_completed_experience(self):
        self.experience.ended_at = timezone.now()
        self.experience.save()
        response = self.client.get(reverse("main:show_experience"))

        self.assertFalse(self.experience.is_ongoing)
        self.assertContains(response, "Selesai")
        self.assertNotContains(response, "Sedang berlangsung")

    def test_experience_card_links_to_its_detail_page(self):
        """Tiap kartu di halaman list Experience mengarah ke URL detailnya."""
        response = self.client.get(reverse("main:show_experience"))
        detail_url = reverse("main:show_experience_detail", args=[self.experience.id])

        self.assertContains(response, f'href="{detail_url}"')

    def test_experience_detail_url_is_accessible_and_uses_correct_template(self):
        detail_url = reverse("main:show_experience_detail", args=[self.experience.id])
        response = self.client.get(detail_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "experience_detail.html")
        self.assertContains(response, self.experience.title)
        self.assertContains(response, self.experience.description)
        self.assertContains(response, f'href="{reverse("main:show_experience")}"')

    def test_experience_detail_returns_404_for_unknown_id(self):
        import uuid

        random_id = uuid.uuid4()
        response = self.client.get(
            reverse("main:show_experience_detail", args=[random_id])
        )

        self.assertEqual(response.status_code, 404)

    def test_create_experience_page_and_valid_submission(self):
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

    def test_delete_experience_requires_post(self):
        delete_url = reverse("main:delete_experience", args=[self.experience.id])
        self.client.get(delete_url)
        self.assertTrue(Experience.objects.filter(pk=self.experience.id).exists())

        response = self.client.post(delete_url)
        self.assertRedirects(response, reverse("main:show_experience"))
        self.assertFalse(Experience.objects.filter(pk=self.experience.id).exists())


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
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "project.html")
        self.assertContains(response, self.project.title)
        self.assertContains(response, self.project.tech_stack)
        self.assertContains(response, self.project.description)

    def test_show_projects_filter(self):
        response = self.client.get(reverse("main:show_projects"), {"title": "Fern"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.title)

        response_not_found = self.client.get(reverse("main:show_projects"), {"title": "NonExistent"})
        self.assertEqual(response_not_found.status_code, 200)
        self.assertContains(response_not_found, "Tidak ada proyek dengan nama tersebut.")

    def test_empty_projects(self):
        Project.objects.all().delete()
        response = self.client.get(reverse("main:show_projects"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Belum ada proyek yang ditambahkan.")

    def test_create_project_view_get(self):
        response = self.client.get(reverse("main:create_project"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "projects_form.html")

    def test_create_project_view_post_valid(self):
        data = {
            "title": "New Web Project",
            "description": "A very cool new web project",
            "tech_stack": "Django, HTML, CSS",
            "project_url": "https://github.com/example/web-project",
            "project_image_url": "https://example.com/img.png",
        }
        response = self.client.post(reverse("main:create_project"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Project.objects.filter(title="New Web Project").exists())

    def test_delete_project(self):
        response = self.client.post(reverse("main:delete_project", kwargs={"project_id": self.project.id}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Project.objects.filter(id=self.project.id).exists())

    def test_get_projects_json(self):
        response = self.client.get(reverse("main:get_projects_json"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertContains(response, "Fern AI Assistant")

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
