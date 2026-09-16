from django import forms
from main.models import Experience

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