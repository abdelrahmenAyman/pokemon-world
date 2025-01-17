from unittest.mock import MagicMock

from django.contrib import auth
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from authentication.serializers import LoginSerializer
from pokemon.factories import UserFactory

User = auth.get_user_model()


def get_user_from_session_info(client: APIClient) -> User:
    """
    A work around to use the session info from the client and check
    if the request was authenticated successfully.
    """
    return auth.get_user(client)


class LoginEndpointTestSuite(APITestCase):
    def setUp(self):
        self.login_path = reverse('auth-login')

        self.existing_user = UserFactory()
        self.existing_user.set_password('password')
        self.existing_user.save()

    def test_login_with_valid_credentials(self):
        data = {
            'email': self.existing_user.email,
            'password': 'password'
        }
        response = self.client.post(path=self.login_path, data=data)

        client_user = get_user_from_session_info(self.client)
        self.assertEqual(200, response.status_code)
        self.assertTrue(client_user.is_authenticated)

    def test_login_with_wrong_password(self):
        data = {
            'email': self.existing_user.email,
            'password': 'wrong password'
        }
        response = self.client.post(path=self.login_path, data=data)

        client_user = get_user_from_session_info(self.client)
        self.assertEqual(400, response.status_code)
        self.assertFalse(client_user.is_authenticated)

    def test_login_with_email_does_not_exist(self):
        data = {
            'email': 'does_not_exist@example.com',
            'password': 'password'
        }
        response = self.client.post(path=self.login_path, data=data)

        client_user = get_user_from_session_info(self.client)
        self.assertEqual(400, response.status_code)
        self.assertFalse(client_user.is_authenticated)


class LoginSerializerTestSuite(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.user.set_password('password')
        self.user.save()

        self.serializer_instance = LoginSerializer(data={'email': self.user.email, 'password': 'password'})

    def test_login_user_is_valid_not_called(self):
        self.assertRaises(Exception, self.serializer_instance.login_user)

    def test_login_serializer_is_valid_called(self):
        self.serializer_instance.context['request'] = MagicMock()
        self.serializer_instance.is_valid()
        try:
            self.serializer_instance.login_user()
        except:
            self.fail('`.login_user()` raised an exception')


class LogoutEndpointTestSuite(APITestCase):

    def setUp(self):
        self.logout_path = reverse('auth-logout')

    def test_logout_anonymous_user(self):
        response = self.client.post(path=self.logout_path)
        self.assertEqual(200, response.status_code)

    def test_logout_logged_in_user(self):
        logged_in_user = UserFactory()
        self.client.force_authenticate(logged_in_user)

        response = self.client.post(path=self.logout_path)
        client_user = get_user_from_session_info(self.client)

        self.assertEqual(200, response.status_code)
        self.assertFalse(client_user.is_authenticated)


class RegisterEndpointTestSuite(APITestCase):

    def setUp(self):
        self.register_path = reverse('auth-register')
        self.valid_data = {
            'email': 'new_email@example.com',
            'password': 'password',
            'confirm_password': 'password'
        }

    def test_register_passwords_does_not_match(self):
        data = {
            'email': 'abdelrahmen@example.com',
            'password': 'password',
            'confirm_password': 'another password'
        }
        response = self.client.post(path=self.register_path, data=data)

        self.assertEqual(400, response.status_code)

    def test_register_with_existing_email(self):
        existing_user = UserFactory()
        data = {
            'email': existing_user.email,
            'password': 'password',
            'confirm_password': 'password'
        }
        response = self.client.post(path=self.register_path, data=data)

        self.assertEqual(400, response.status_code)

    def test_register_with_valid_data_user_is_created(self):
        response = self.client.post(path=self.register_path, data=self.valid_data)

        self.assertEqual(201, response.status_code)
        self.assertEqual(1, User.objects.count())

    def test_register_with_valid_data_username_is_set_to_email(self):
        response = self.client.post(path=self.register_path, data=self.valid_data)
        created_user = User.objects.get(email=self.valid_data.get('email'))

        self.assertEqual(201, response.status_code)
        self.assertEqual(created_user.email, created_user.username)
