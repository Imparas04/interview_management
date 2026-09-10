from django.db import models
from candidates.models import CandidateProfile
from jobs.models import JobRole
from resumes.models import Resume


class Application(models.Model):
    """
    One candidate applying to one job. unique_together prevents a
    candidate from applying to the same job twice - they'd need to
    withdraw (not implemented) rather than create duplicate rows.

    `status` choices exactly mirror the workflow diagram in the spec.
    The ONLY place allowed to change this field's value in application
    code is transitions.py's transition_application_status() - views
    must go through that function, never instance.status = X directly,
    so the state machine rule is enforced in exactly one place.
    """

    class Status(models.TextChoices):
        APPLIED = 'applied', 'Applied'
        ATS_ANALYSIS = 'ats_analysis', 'ATS Analysis'
        SHORTLISTED = 'shortlisted', 'Shortlisted'
        HR_SCREENING = 'hr_screening', 'HR Screening'
        TECHNICAL_ROUND = 'technical_round', 'Technical Round'
        CODING_ROUND = 'coding_round', 'Coding Round'
        MANAGERIAL_ROUND = 'managerial_round', 'Managerial Round'
        FINAL_HR = 'final_hr', 'Final HR'
        SELECTED = 'selected', 'Selected'
        REJECTED = 'rejected', 'Rejected'

    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(JobRole, on_delete=models.CASCADE, related_name='applications')
    resume = models.ForeignKey(Resume, on_delete=models.PROTECT, related_name='applications')

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPLIED)

    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('candidate', 'job')
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.candidate.user.username} -> {self.job.title} ({self.status})"
