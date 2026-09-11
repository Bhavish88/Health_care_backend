from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class AuthenticationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = '/api/auth/register/'
        self.login_url = '/api/auth/login/'
        self.user_data = {
            'name': 'Test Doctor User',
            'email': 'doctor.user@example.com',
            'password': 'StrongPassword123!'
        }

    def test_register_user_success(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'doctor.user@example.com')
        self.assertEqual(response.data['user']['name'], 'Test Doctor User')
        # Ensure password is not returned in response
        self.assertNotIn('password', response.data['user'])

        # Verify password is properly hashed in database
        user = User.objects.get(email='doctor.user@example.com')
        self.assertTrue(user.check_password('StrongPassword123!'))

    def test_register_duplicate_email(self):
        # Register first user
        self.client.post(self.register_url, self.user_data, format='json')
        # Attempt to register second user with same email
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data['errors'])

    def test_register_missing_fields(self):
        response = self.client.post(self.register_url, {'email': 'incomplete@example.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_success(self):
        # Register user first
        self.client.post(self.register_url, self.user_data, format='json')

        login_payload = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        response = self.client.post(self.login_url, login_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertIn('access', response.data['tokens'])
        self.assertIn('refresh', response.data['tokens'])

    def test_login_wrong_password(self):
        self.client.post(self.register_url, self.user_data, format='json')

        login_payload = {
            'email': self.user_data['email'],
            'password': 'WrongPassword999'
        }
        response = self.client.post(self.login_url, login_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_non_existent_email(self):
        login_payload = {
            'email': 'nobody@example.com',
            'password': 'SomePassword123'
        }
        response = self.client.post(self.login_url, login_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
