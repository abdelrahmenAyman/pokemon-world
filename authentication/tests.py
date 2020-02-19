from django.contrib import auth
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from authentication.serializers import LoginSerializer
from pokemon.factories import UserFactory

User = auth.get_user_model()


class LoginEndpointTestSuite(APITestCase):
    def setUp(self):
        self.login_path = reverse('auth-login')

        self.existing_user = UserFactory()
        self.existing_user.set_password('password')
        self.existing_user.save()

    def get_user_from_session_info(self) -> User:
        """
        A work around to use the session info from the client and check
        if the request was authenticated successfully.
        """
        return auth.get_user(self.client)

    def test_login_with_valid_credentials(self):
        data = {
            'email': self.existing_user.email,
            'password': 'password'
        }
        response = self.client.post(path=self.login_path, data=data)

        client_user = self.get_user_from_session_info()
        self.assertEqual(200, response.status_code)
        self.assertTrue(client_user.is_authenticated)

    def test_login_with_wrong_password(self):
        data = {
            'email': self.existing_user.email,
            'password': 'wrong password'
        }
        response = self.client.post(path=self.login_path, data=data)

        client_user = self.get_user_from_session_info()
        self.assertEqual(400, response.status_code)
        self.assertFalse(client_user.is_authenticated)

    def test_login_with_email_does_not_exist(self):
        data = {
            'email': 'does_not_exist@example.com',
            'password': 'password'
        }
        response = self.client.post(path=self.login_path, data=data)

        client_user = self.get_user_from_session_info()
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
        self.serializer_instance.is_valid()
        try:
            self.serializer_instance.login_user()
        except KeyError:
            # the function execution passed the assertion successfully
            pass
        except:
            self.fail('`.login_user()` raised an exception')
