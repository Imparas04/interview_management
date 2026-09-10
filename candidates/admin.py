from django.contrib import admin
from .models import CandidateProfile


@admin.register(CandidateProfile)
class CandidateProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'recommended_department', 'created_at')
    search_fields = ('user__username', 'user__email')
