from django.contrib import admin

from .models import Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'author', 'publish_date', 'domain', 'is_active', 'updated_at']
    list_filter = ['domain', 'is_active']
    search_fields = ['name', 'author', 'description']
