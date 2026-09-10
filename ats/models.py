from django.db import models
from candidates.models import CandidateProfile
from resumes.models import Resume
from jobs.models import JobRole


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


class ATSResult(models.Model):
    """
    One ATS analysis of a specific (resume, job) pair. Kept independent of
    Application for now (Applications module comes in Phase 10) - Phase 10
    will link an Application to its ATSResult via this same (resume, job)
    pairing rather than duplicating the calculation.

    unique_together means re-scoring the same resume against the same job
    updates this row (via update_or_create) instead of piling up duplicate
    historical scores - we only care about the latest analysis.
    """
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE, related_name='ats_results')
    job = models.ForeignKey(JobRole, on_delete=models.CASCADE, related_name='ats_results')

    skills_match_pct = models.FloatField()
    experience_match_pct = models.FloatField()
    education_match_pct = models.FloatField()
    projects_pct = models.FloatField()
    certifications_pct = models.FloatField()
    keywords_pct = models.FloatField()
    overall_score = models.FloatField()

    # Full breakdown - matched/missing skills, years found, keywords matched,
    # etc. Stored once at calculation time, never recomputed on read.
    explanation = models.JSONField()

    calculated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('resume', 'job')
        ordering = ['-overall_score']

    def __str__(self):
        return f"ATS {self.overall_score}% - {self.resume.candidate.user.username} / {self.job.title}"
