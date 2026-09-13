from django.shortcuts import render

from main.models import Experience, Education


def show_main(request):
    context = {
        "name": "Muhammad Sabri",
        "npm": "2506623793",
        "study_program": "S1 Ilmu Komputer",
        "bio": (
            "Mahasiswa Ilmu Komputer Universitas Indonesia yang tertarik "
            "pada sains data dan kecerdasan buatan."
        ),
    }
    return render(request, "index.html", context)


def show_experience(request):
    context = {
        "name": "Muhammad Sabri",
        "experience_list": Experience.objects.all(),
    }
    return render(request, "experience.html", context)

def show_education(request):
    context = {
        "name": "Muhammad Sabri",
        "education_list": Education.objects.all(),
    }
    return render(request, "education.html", context)