from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from digimon.models import Digimon
from pokemon.factories import UserFactory


class DigimonCreateActionTestSuite(APITestCase):

    def setUp(self):
        self.create_path = reverse('digimon-list')
        self.valid_creation_data = {
            'name': 'Mighty Digimon',
            'description': 'Super cool digimon',
            'weight': 68
        }

    def test_create_digimon_as_anonymous_user(self):
        response = self.client.post(path=self.create_path, data=self.valid_creation_data)
        self.assertEqual(401, response.status_code)
        self.assertEqual(0, Digimon.objects.count())

    def test_create_digimon_as_authenticated_user(self):
        self.client.force_authenticate(UserFactory())
        response = self.client.post(path=self.create_path, data=self.valid_creation_data)

        self.assertEqual(201, response.status_code)
        self.assertEqual(1, Digimon.objects.count())

    def test_create_digimon_creator_is_set_to_request_user(self):
        request_user = UserFactory()
        self.client.force_authenticate(request_user)
        response = self.client.post(path=self.create_path, data=self.valid_creation_data)

        self.assertEqual(201, response.status_code)
        self.assertEqual(request_user, Digimon.objects.first().creator)
