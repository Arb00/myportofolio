from django.utils.html import strip_tags
from rest_framework import serializers

from main.models import Project


class ProjectSerializer(serializers.ModelSerializer):
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id", "title", "description", "tech_stack",
            "project_url", "project_image_url",
            "star_count", "is_starred", "starred_by_names",
        ]
        read_only_fields = ["id"]

    # Aturan sama dengan ProjectForm, karena input API tidak melewati form
    def validate_title(self, value):
        value = strip_tags(value).strip()
        if not value:
            raise serializers.ValidationError("Nama proyek tidak boleh kosong atau hanya berisi tag HTML.")
        return value

    def validate_description(self, value):
        return strip_tags(value)

    def validate_tech_stack(self, value):
        return strip_tags(value)

    # starred_by.all() memakai hasil prefetch_related, jadi tidak menambah query per kartu
    def get_star_count(self, obj):
        return len(obj.starred_by.all())

    def get_is_starred(self, obj):
        request = self.context.get("request")
        if request is None or not request.user.is_authenticated:
            return False
        return request.user in obj.starred_by.all()

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())
