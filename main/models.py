import uuid
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class Experience(models.Model):
    EXPERIENCE_CHOICES = [
        ('internship', 'Internship'),
        ('research', 'Research'),
        ('volunteer', 'Volunteer'),
        ('part-time', 'Part-Time'),
        ('full-time', 'Full-Time'),
        ('freelance', 'Freelance'),
        ('seasonal', 'Seasonal')
    ]
    stars = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="starred_experiences",
        blank=True,
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES, default='full-time')
    thumbnail = models.URLField(blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.title
    
    @property
    def is_ongoing(self):
        return self.ended_at is None

class Education(models.Model):
    EDUCATION_LEVEL_CHOICES = [
        ('S1', 'Sarjana'),
        ('SMA', 'SMA'),
        ('SMP', 'SMP'),
        ('SD', 'SD'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.CharField(max_length=255)
    level = models.CharField(max_length=10, choices=EDUCATION_LEVEL_CHOICES)
    field_of_study = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='education_logos/', blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    started_at = models.DateField()
    ended_at = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.institution


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    tech_stack = models.CharField(max_length=255)
    project_url = models.URLField(blank=True)
    project_image_url = models.URLField(blank=True, max_length=500)
    starred_by = models.ManyToManyField(User, related_name="starred_projects", blank=True)

    def __str__(self):
        return self.title


class Skill(models.Model):
    CATEGORY_CHOICES = [
        ('language', 'Bahasa Pemrograman'),
        ('framework', 'Framework & Library'),
        ('tool', 'Tools'),
        ('other', 'Lainnya'),
    ]
    LEVEL_CHOICES = [
        (1, 'Pemula'),
        (2, 'Menengah'),
        (3, 'Mahir'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='language')
    level = models.PositiveSmallIntegerField(choices=LEVEL_CHOICES, default=1)

    class Meta:
        ordering = ['category', '-level', 'name']

    def __str__(self):
        return self.name


class Message(models.Model):
    """Pesan dari form Contact di beranda; dibaca lewat admin."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} <{self.email}>"
