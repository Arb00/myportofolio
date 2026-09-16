from django.contrib import messages
from django.core import serializers
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from main.forms import ExperienceForm
from main.models import Education, Experience


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
