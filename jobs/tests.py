from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from departments.models import Department
from jobs.models import JobRole

User = get_user_model()


class JobTests(APITestCase):
    def setUp(self):
        self.hr = User.objects.create_user(username='hr1', password='pass12345', role=User.Role.HR)
        self.candidate = User.objects.create_user(username='cand1', password='pass12345', role=User.Role.CANDIDATE)
        self.dept = Department.objects.create(name='Python Development')

    def test_hr_can_create_job_with_nested_skills(self):
        self.client.force_authenticate(self.hr)
        response = self.client.post('/api/jobs/', {
            'title': 'Python Developer',
            'department': self.dept.id,
            'description': 'Backend role',
            'experience_min': 0,
            'experience_max': 2,
            'num_openings': 2,
            'job_type': 'full_time',
            'status': 'open',
            'required_skills': [{'skill_name': 'Python', 'weight': 3}],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(response.data['required_skills']), 1)

    def test_candidate_only_sees_open_jobs(self):
        JobRole.objects.create(title='Draft Job', department=self.dept, description='x', status=JobRole.Status.DRAFT)
        JobRole.objects.create(title='Open Job', department=self.dept, description='x', status=JobRole.Status.OPEN)

        self.client.force_authenticate(self.candidate)
        response = self.client.get('/api/jobs/')
        titles = [j['title'] for j in response.data['results']] if 'results' in response.data else [j['title'] for j in response.data]
        self.assertIn('Open Job', titles)
        self.assertNotIn('Draft Job', titles)
