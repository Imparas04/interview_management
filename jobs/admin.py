from django.contrib import admin
from .models import JobRole, JobSkill


class JobSkillInline(admin.TabularInline):
    model = JobSkill
    extra = 1


@admin.register(JobRole)
class JobRoleAdmin(admin.ModelAdmin):
    list_display = ('title', 'department', 'status', 'job_type', 'num_openings', 'created_at')
    list_filter = ('status', 'job_type', 'department')
    search_fields = ('title', 'location')
    inlines = [JobSkillInline]
