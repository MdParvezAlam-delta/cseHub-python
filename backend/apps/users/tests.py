from django.test import TestCase
from django.test.utils import override_settings
from rest_framework.test import APIClient

from .models import User


@override_settings(LOCAL_AUTH_ENABLED=True)
class LocalPasswordAuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.credentials = {
            'name': 'Test User',
            'email': 'dummy-account@example.invalid',
            'password': 'DummyPassword123!',
        }

    def test_signup_and_signin_work_without_email_confirmation(self):
        signup = self.client.post('/api/auth/signup/', self.credentials, format='json')

        self.assertEqual(signup.status_code, 201)
        user = User.objects.get(email=self.credentials['email'])
        self.assertTrue(user.check_password(self.credentials['password']))
        self.assertNotEqual(user.password, self.credentials['password'])
        self.assertEqual(signup.data['user']['display_name'], self.credentials['name'])

        signin = self.client.post(
            '/api/auth/signin/',
            {'email': self.credentials['email'], 'password': self.credentials['password']},
            format='json',
        )
        self.assertEqual(signin.status_code, 200)
        self.assertEqual(signin.data['user']['id'], user.pk)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {signin.data['access_token']}"
        )
        profile = self.client.get('/api/auth/me/')
        self.assertEqual(profile.status_code, 200)
        self.assertEqual(profile.data['email'], self.credentials['email'])

    def test_signup_rejects_duplicate_email_and_signin_rejects_wrong_password(self):
        self.client.post('/api/auth/signup/', self.credentials, format='json')
        duplicate = self.client.post('/api/auth/signup/', self.credentials, format='json')
        wrong_password = self.client.post(
            '/api/auth/signin/',
            {'email': self.credentials['email'], 'password': 'WrongPassword123!'},
            format='json',
        )

        self.assertEqual(duplicate.status_code, 400)
        self.assertEqual(wrong_password.status_code, 400)

    @override_settings(LOCAL_AUTH_ENABLED=False)
    def test_local_auth_is_disabled_when_not_enabled(self):
        response = self.client.post('/api/auth/signup/', self.credentials, format='json')
        self.assertEqual(response.status_code, 404)
