from django.contrib import admin
from .models import Resume


@admin.register(Resume)
class ResumeAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'candidate', 'file_type', 'parsing_status', 'uploaded_at')
    list_filter = ('parsing_status', 'file_type')
    search_fields = ('original_filename', 'candidate__user__username', 'parsed_email')
