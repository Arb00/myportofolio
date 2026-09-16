from django.urls import path
from main.views import (
    show_main,
    show_experience,
    show_experience_detail,
    create_experience,
    delete_experience,
    get_experience_json,
    get_experience_xml,
    get_experience_json_by_id,
    get_experience_xml_by_id,
    show_education,
)

app_name = "main"

urlpatterns = [
    path("", show_main, name="show_main"),
    path("experience/", show_experience, name="show_experience"),
    path("experience/add/", create_experience, name="create_experience"),
    path("experience/<uuid:id>/", show_experience_detail, name="show_experience_detail"),
    path("experience/<uuid:experience_id>/delete/", delete_experience, name="delete_experience"),
    path("api/experience/", get_experience_json, name="get_experience_json"),
    path("api/experience/xml/", get_experience_xml, name="get_experience_xml"),
    path(
        "api/experience/<uuid:experience_id>/",
        get_experience_json_by_id,
        name="get_experience_json_by_id",
    ),
    path(
        "api/experience/xml/<uuid:experience_id>/",
        get_experience_xml_by_id,
        name="get_experience_xml_by_id",
    ),
    path("education/", show_education, name="show_education"),
]
