from django.conf import settings
from django.db import models
from departments.models import Department


class CandidateProfile(models.Model):
    """
    One profile per candidate user (OneToOne - a candidate has exactly one
    profile, never zero after first use, never more than one). Kept separate
    from the User model itself because User is shared across all 4 roles
    and we don't want HR/Interviewer/Admin accounts carrying candidate-only
    fields like phone/address/recommended department.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='candidate_profile'
    )
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    summary = models.TextField(blank=True, help_text="Short professional summary")
    linkedin_url = models.URLField(blank=True)
    portfolio_url = models.URLField(blank=True)

    # Filled in automatically by the ATS engine in a later phase - candidate
    # never sets this directly, so it's read-only at the serializer level.
    recommended_department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='recommended_candidates'
    )
    recommended_department_confidence = models.FloatField(null=True, blank=True)
    recommended_department_explanation = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profile: {self.user.username}"
