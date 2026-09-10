from django.contrib import admin
from .models import CandidateSkill


@admin.register(CandidateSkill)
class CandidateSkillAdmin(admin.ModelAdmin):
    list_display = ('skill_name', 'candidate', 'source_resume', 'extracted_at')
    search_fields = ('skill_name', 'candidate__user__username')
    list_filter = ('skill_name',)
