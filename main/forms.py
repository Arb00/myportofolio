from django import forms
from main.models import Experience, Project


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = [
            "title",
            "category",
            "description",
            "thumbnail",
            "ended_at",
        ]
        labels = {
            "title": "Judul Pengalaman",
            "category": "Kategori / Jenis",
            "description": "Deskripsi",
            "thumbnail": "URL Gambar / Thumbnail",
            "ended_at": "Tanggal Selesai (Kosongkan jika masih berlangsung)",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "misal: Lab Assistant MPKT-G",
                    "maxlength": 255,
                }
            ),
            "category": forms.Select(
                attrs={
                    "class": "form-select",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "placeholder": "Ceritakan peran dan pengalamanmu...",
                    "rows": 3,
                }
            ),
            "thumbnail": forms.URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=FILE_ID&sz=w1000",
                }
            ),
            "ended_at": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                }
            ),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = [
            "title",
            "description",
            "tech_stack",
            "project_url",
            "project_image_url",
        ]
        labels = {
            "title": "Nama Proyek",
            "description": "Deskripsi Proyek",
            "tech_stack": "Teknologi yang Digunakan",
            "project_url": "URL Proyek",
            "project_image_url": "URL Gambar Proyek",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "placeholder": "misal: Portfolio Website",
                    "maxlength": 255,
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "placeholder": "Ceritakan Proyekmu...",
                    "rows": 3,
                }
            ),
            "tech_stack": forms.TextInput(
                attrs={
                    "placeholder": "misal: Django, Python, HTML, CSS",
                    "maxlength": 255,
                }
            ),
            "project_url": forms.URLInput(
                attrs={
                    "placeholder": "https://github.com/username/project",
                }
            ),
            "project_image_url": forms.URLInput(
                attrs={
                    "placeholder": "https://drive.google.com/thumbnail?id=...&sz=w1000",
                }
            ),
        }
