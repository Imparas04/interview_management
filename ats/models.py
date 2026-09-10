from django.db import models
from candidates.models import CandidateProfile
from resumes.models import Resume


class CandidateSkill(models.Model):
    """
    One row per skill extracted for a candidate. Represents the candidate's
    CURRENT skill set as of their most recent resume extraction - when a
    candidate re-uploads and re-extracts, old rows are replaced (see
    extract_and_save_skills in views.py) rather than piling up duplicates
    from every past resume.
    """
    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='skills')
    skill_name = models.CharField(max_length=100)
    source_resume = models.ForeignKey(Resume, on_delete=models.SET_NULL, null=True, related_name='extracted_skills')
    extracted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('candidate', 'skill_name')
        ordering = ['skill_name']

    def __str__(self):
        return f"{self.skill_name} - {self.candidate.user.username}"
