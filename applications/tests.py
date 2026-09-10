from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model
from candidates.models import CandidateProfile
from departments.models import Department
from jobs.models import JobRole
from resumes.models import Resume
from .models import Application
from .transitions import transition_application_status

User = get_user_model()


class ApplicationStateMachineTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='cand1', password='pass12345', role=User.Role.CANDIDATE)
        candidate = CandidateProfile.objects.create(user=user)
        dept = Department.objects.create(name='Python Development')
        job = JobRole.objects.create(title='Python Dev', department=dept, description='x')
        resume = Resume.objects.create(candidate=candidate, original_filename='r.pdf', file_type='pdf')
        self.application = Application.objects.create(candidate=candidate, job=job, resume=resume)

    def test_valid_transition_succeeds(self):
        transition_application_status(self.application, Application.Status.ATS_ANALYSIS)
        self.assertEqual(self.application.status, Application.Status.ATS_ANALYSIS)

    def test_skipping_steps_is_rejected(self):
        """Applied -> Selected directly must be rejected; must go through the full workflow."""
        with self.assertRaises(ValidationError):
            transition_application_status(self.application, Application.Status.SELECTED)

    def test_rejected_is_terminal(self):
        transition_application_status(self.application, Application.Status.REJECTED)
        with self.assertRaises(ValidationError):
            transition_application_status(self.application, Application.Status.SHORTLISTED)
