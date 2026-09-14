from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import date

from main.models import Experience, Education


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