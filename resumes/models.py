from django.db import models
from candidates.models import CandidateProfile
from .validators import validate_resume_file, resume_upload_path


class Resume(models.Model):
    """
    A single uploaded resume file. A candidate can upload more than one
    over time (re-uploading an updated resume) - we keep history rather
    than overwriting, since a past Application may reference an older
    Resume and we don't want its parsed data to silently change under it.
    """

    class ParsingStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        SUCCESS = 'success', 'Success'
        FAILED = 'failed', 'Failed'

    candidate = models.ForeignKey(CandidateProfile, on_delete=models.CASCADE, related_name='resumes')

    file = models.FileField(upload_to=resume_upload_path, validators=[validate_resume_file])
    original_filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=10)  # 'pdf' or 'docx'

    # Raw extracted text - stored once, reused by Phase 7 (skill extraction)
    # and Phase 8 (ATS scoring) so we never have to re-open/re-parse the
    # file for every downstream calculation.
    parsed_text = models.TextField(blank=True)

    parsed_name = models.CharField(max_length=150, blank=True)
    parsed_email = models.EmailField(blank=True)
    parsed_phone = models.CharField(max_length=20, blank=True)

    parsing_status = models.CharField(max_length=10, choices=ParsingStatus.choices, default=ParsingStatus.PENDING)
    parsing_error = models.TextField(blank=True)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Resume({self.original_filename}) - {self.candidate.user.username}"
