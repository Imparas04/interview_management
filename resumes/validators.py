import os
import uuid
from django.core.exceptions import ValidationError

ALLOWED_EXTENSIONS = ['.pdf', '.docx']
MAX_FILE_SIZE_MB = 5


def validate_resume_file(file):
    """
    Validates extension and size. We deliberately do NOT trust the
    original filename beyond reading its extension for this check -
    the actual stored filename is generated separately (see
    resume_upload_path) so nothing from the client ever reaches the
    filesystem path directly.
    """
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f"Unsupported file type '{ext}'. Only PDF and DOCX are allowed.")

    max_bytes = MAX_FILE_SIZE_MB * 1024 * 1024
    if file.size > max_bytes:
        raise ValidationError(f"File too large. Maximum allowed size is {MAX_FILE_SIZE_MB}MB.")


def resume_upload_path(instance, filename):
    """
    Generates a random, safe filename instead of using the client-supplied
    one. Prevents path traversal (e.g. '../../settings.py') and filename
    collisions between different candidates' uploads.
    """
    ext = os.path.splitext(filename)[1].lower()
    safe_name = f"{uuid.uuid4().hex}{ext}"
    return f"resumes/{instance.candidate.user.id}/{safe_name}"
