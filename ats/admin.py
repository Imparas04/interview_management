from django.contrib import admin
from .models import CandidateSkill, ATSResult


@admin.register(CandidateSkill)
class CandidateSkillAdmin(admin.ModelAdmin):
    list_display = ('skill_name', 'candidate', 'source_resume', 'extracted_at')
    search_fields = ('skill_name', 'candidate__user__username')
    list_filter = ('skill_name',)


@admin.register(ATSResult)
class ATSResultAdmin(admin.ModelAdmin):
    list_display = ('resume', 'job', 'overall_score', 'skills_match_pct', 'calculated_at')
    list_filter = ('job',)
    search_fields = ('resume__candidate__user__username', 'job__title')
