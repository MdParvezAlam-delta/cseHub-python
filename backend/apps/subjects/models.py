from django.db import models
from django.utils import timezone


class Subject(models.Model):
    DOMAINS = [
        ('DSA', 'Data Structures and Algorithms'),
        ('Web Development', 'Web Development'),
        ('Machine Learning', 'Machine Learning'),
        ('Systems', 'Systems'),
        ('Programming', 'Programming'),
    ]

    name = models.CharField(max_length=100, unique=True)
    author = models.CharField(max_length=100, default='CSEHub Admin')
    publish_date = models.DateField(default=timezone.localdate)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='school')
    domain = models.CharField(max_length=80, choices=DOMAINS, default='DSA')
    content_markdown = models.TextField(blank=True)
    code_snippets = models.JSONField(default=list, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
