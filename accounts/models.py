from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model. We extend AbstractUser (not AbstractBaseUser) because
    we still want Django's built-in username/password/email fields and
    permission machinery - we're only adding one thing: a role.
    """

    class Role(models.TextChoices):
        ADMIN = 'admin', 'Admin'
        HR = 'hr', 'HR / Recruiter'
        INTERVIEWER = 'interviewer', 'Interviewer'
        CANDIDATE = 'candidate', 'Candidate'

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CANDIDATE,
    )

    def __str__(self):
        return f"{self.username} ({self.role})"
