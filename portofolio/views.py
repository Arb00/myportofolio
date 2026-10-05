from django.shortcuts import render


def landing_page(request):
    return render(request, "index.html")


def experience_detail(request):
    return render(request, "experience.html")