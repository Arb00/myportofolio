from django.contrib import admin
from main.models import Education, Experience, Message, Project, Skill

admin.site.register(Experience)
admin.site.register(Education)
admin.site.register(Project)


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "level")
    list_filter = ("category", "level")
    search_fields = ("name",)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email", "message")
    readonly_fields = ("name", "email", "message", "created_at")

    # Pesan hanya masuk lewat form Contact, tidak dibuat dari admin
    def has_add_permission(self, request):
        return False
