from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class AuthTests(APITestCase):
    def test_register_creates_candidate_role_only(self):
        """
        A registration request trying to sneak in role=admin must be
        ignored - RegisterSerializer hardcodes CANDIDATE regardless of
        what's in the request body.
        """
        response = self.client.post('/api/auth/register/', {
            'username': 'sneaky',
            'email': 'sneaky@test.com',
            'password': 'testpass123',
            'role': 'admin',  # should be ignored
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.get(username='sneaky')
        self.assertEqual(user.role, User.Role.CANDIDATE)

    def test_login_returns_role(self):
        User.objects.create_user(username='rahul', password='pass12345', role=User.Role.HR)
        response = self.client.post('/api/auth/login/', {'username': 'rahul', 'password': 'pass12345'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['role'], 'hr')
        self.assertIn('access', response.data)

    def test_me_requires_authentication(self):
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
