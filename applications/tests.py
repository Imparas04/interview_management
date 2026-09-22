from django.core.exceptions import ValidationError
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from candidates.models import CandidateProfile
from departments.models import Department
from jobs.models import JobRole, JobSkill
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


class AutoProcessApplicationsTests(APITestCase):
    """Covers the auto-shortlist/auto-reject endpoint end-to-end."""

    def setUp(self):
        self.hr = User.objects.create_user(username='hr1', password='pass12345', role=User.Role.HR)
        cand_user = User.objects.create_user(username='cand1', password='pass12345', role=User.Role.CANDIDATE)
        self.candidate = CandidateProfile.objects.create(user=cand_user)
        self.dept = Department.objects.create(name='Python Development')
        self.job = JobRole.objects.create(title='Python Dev', department=self.dept, description='x')
        JobSkill.objects.create(job_role=self.job, skill_name='Python', weight=3)

        self.resume = Resume.objects.create(
            candidate=self.candidate, original_filename='r.pdf', file_type='pdf',
            parsed_text="Experienced in Python and Django. 2 years experience. Project: built an API.",
            parsing_status=Resume.ParsingStatus.SUCCESS,
        )
        self.application = Application.objects.create(candidate=self.candidate, job=self.job, resume=self.resume)

    def test_non_hr_cannot_auto_process(self):
        self.client.force_authenticate(User.objects.get(username='cand1'))
        response = self.client.post('/api/applications/auto-process/', {'job_id': self.job.id}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_high_score_gets_shortlisted(self):
        self.client.force_authenticate(self.hr)
        response = self.client.post(
            '/api/applications/auto-process/',
            {'job_id': self.job.id, 'shortlist_threshold': 10},  # low bar so this resume clears it
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, Application.Status.SHORTLISTED)
        self.assertEqual(response.data['shortlisted'], 1)

    def test_low_score_gets_rejected(self):
        self.client.force_authenticate(self.hr)
        response = self.client.post(
            '/api/applications/auto-process/',
            {'job_id': self.job.id, 'shortlist_threshold': 99.9},  # high bar this resume won't clear
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.application.refresh_from_db()
        self.assertEqual(self.application.status, Application.Status.REJECTED)
        self.assertEqual(response.data['rejected'], 1)
