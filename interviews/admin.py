from django.contrib import admin
from .models import InterviewRound, Interview, InterviewFeedback


@admin.register(InterviewRound)
class InterviewRoundAdmin(admin.ModelAdmin):
    list_display = ('order', 'name')


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('application', 'round', 'interviewer', 'scheduled_date', 'scheduled_time', 'status')
    list_filter = ('status', 'round')


@admin.register(InterviewFeedback)
class InterviewFeedbackAdmin(admin.ModelAdmin):
    list_display = ('interview', 'overall_score', 'recommendation', 'submitted_by', 'created_at')
