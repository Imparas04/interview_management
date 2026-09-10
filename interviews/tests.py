from datetime import date, time
from django.test import TestCase
from django.contrib.auth import get_user_model
from candidates.models import CandidateProfile
from departments.models import Department
from jobs.models import JobRole
from resumes.models import Resume
from applications.models import Application
from .models import InterviewRound, Interview
from .conflicts import has_conflict

User = get_user_model()


class ConflictDetectionTests(TestCase):
    def setUp(self):
        self.interviewer = User.objects.create_user(username='intv1', password='pass12345', role=User.Role.INTERVIEWER)
        cand_user = User.objects.create_user(username='cand1', password='pass12345', role=User.Role.CANDIDATE)
        candidate = CandidateProfile.objects.create(user=cand_user)
        dept = Department.objects.create(name='Python Development')
        job = JobRole.objects.create(title='Python Dev', department=dept, description='x')
        resume = Resume.objects.create(candidate=candidate, original_filename='r.pdf', file_type='pdf')
        self.application = Application.objects.create(candidate=candidate, job=job, resume=resume)
        self.round = InterviewRound.objects.create(name='Technical Interview', order=2)

        Interview.objects.create(
            application=self.application, round=self.round, interviewer=self.interviewer,
            scheduled_date=date(2026, 9, 20), scheduled_time=time(11, 0), duration_minutes=60,
        )

    def test_overlapping_time_is_a_conflict(self):
        conflict, _ = has_conflict(self.interviewer, date(2026, 9, 20), time(11, 30), 30)
        self.assertTrue(conflict)

    def test_non_overlapping_time_is_not_a_conflict(self):
        conflict, _ = has_conflict(self.interviewer, date(2026, 9, 20), time(13, 0), 30)
        self.assertFalse(conflict)

    def test_different_day_is_not_a_conflict(self):
        conflict, _ = has_conflict(self.interviewer, date(2026, 9, 21), time(11, 0), 60)
        self.assertFalse(conflict)
