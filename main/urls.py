from django.urls import path
from main.views import (
    create_experience,
    create_project,
    delete_experience,
    delete_project,
    edit_project,

    get_experience_json,
    get_experience_json_by_id,
    get_experience_xml,
    get_experience_xml_by_id,
    get_project_json_by_id,
    get_project_xml_by_id,
    get_projects_json,
    get_projects_xml,
    show_education,
    show_experience,
    show_experience_detail,
    show_main,
    show_projects,
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
    path("projects/", show_projects, name="show_projects"),
    path("projects/add/", create_project, name="create_project"),
    path("projects/<uuid:project_id>/edit/", edit_project, name="edit_project"),
    path("projects/<uuid:project_id>/delete/", delete_project, name="delete_project"),
    path("api/projects/", get_projects_json, name="get_projects_json"),
    path("api/projects/xml/", get_projects_xml, name="get_projects_xml"),
    path(
        "api/projects/<uuid:project_id>/",
        get_project_json_by_id,
        name="get_project_json_by_id",
    ),
    path(
        "api/projects/xml/<uuid:project_id>/",
        get_project_xml_by_id,
        name="get_project_xml_by_id",
    ),
]
