from django.conf import settings
from django.db import models
from departments.models import Department


class JobRole(models.Model):
    """
    A job vacancy posted by HR/Admin. experience_min/max are separate
    integer fields (not a free-text "0-2 Years" string) so later phases
    can do numeric comparisons against a candidate's parsed experience
    without re-parsing text every time.
    """

    class JobType(models.TextChoices):
        FULL_TIME = 'full_time', 'Full Time'
        PART_TIME = 'part_time', 'Part Time'
        INTERNSHIP = 'internship', 'Internship'
        CONTRACT = 'contract', 'Contract'

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        OPEN = 'open', 'Open'
        CLOSED = 'closed', 'Closed'

    title = models.CharField(max_length=150)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='job_roles')
    description = models.TextField()

    experience_min = models.PositiveIntegerField(default=0, help_text="Minimum years of experience")
    experience_max = models.PositiveIntegerField(default=0, help_text="Maximum years of experience")

    education_required = models.CharField(max_length=200, blank=True)
    keywords = models.TextField(blank=True, help_text="Comma-separated keywords for ATS keyword matching")

    num_openings = models.PositiveIntegerField(default=1)
    location = models.CharField(max_length=150, blank=True)
    job_type = models.CharField(max_length=20, choices=JobType.choices, default=JobType.FULL_TIME)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.DRAFT)

    application_deadline = models.DateField(null=True, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='created_jobs'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.department.name})"


class JobSkill(models.Model):
    """
    One required skill for a job, with a weight controlling how much it
    matters in ATS skill-match scoring (Phase 8). Kept as its own table
    (not a comma-separated field on JobRole) so scoring code can query
    and weight each skill individually instead of re-parsing a string
    every time a resume is scored.
    """
    job_role = models.ForeignKey(JobRole, on_delete=models.CASCADE, related_name='required_skills')
    skill_name = models.CharField(max_length=100)
    weight = models.PositiveIntegerField(default=1, help_text="Relative importance of this skill")

    class Meta:
        unique_together = ('job_role', 'skill_name')

    def __str__(self):
        return f"{self.skill_name} (weight={self.weight}) - {self.job_role.title}"
