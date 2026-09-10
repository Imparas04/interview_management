from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class DepartmentPermissionTests(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin1', password='pass12345', role=User.Role.ADMIN)
        self.candidate = User.objects.create_user(username='cand1', password='pass12345', role=User.Role.CANDIDATE)

    def test_candidate_cannot_create_department(self):
        self.client.force_authenticate(self.candidate)
        response = self.client.post('/api/departments/', {'name': 'Blockchain'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_department(self):
        self.client.force_authenticate(self.admin)
        response = self.client.post('/api/departments/', {'name': 'Blockchain'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_any_authenticated_user_can_view_departments(self):
        self.client.force_authenticate(self.candidate)
        response = self.client.get('/api/departments/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
