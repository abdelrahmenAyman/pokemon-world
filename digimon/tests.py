from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from digimon.factories import DigimonFactory
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
        self.authenticated_user = UserFactory()
        self.client.force_authenticate(self.authenticated_user)

    def test_create_digimon_as_anonymous_user(self):
        self.client.logout()
        response = self.client.post(path=self.create_path, data=self.valid_creation_data)
        self.assertEqual(401, response.status_code)
        self.assertEqual(0, Digimon.objects.count())

    def test_create_digimon_as_authenticated_user(self):
        response = self.client.post(path=self.create_path, data=self.valid_creation_data)

        self.assertEqual(201, response.status_code)
        self.assertEqual(1, Digimon.objects.count())

    def test_create_digimon_creator_is_set_to_request_user(self):
        response = self.client.post(path=self.create_path, data=self.valid_creation_data)

        self.assertEqual(201, response.status_code)
        self.assertEqual(self.authenticated_user, Digimon.objects.first().creator)

    def test_create_digimon_with_duplicate_name(self):
        existing_digimon = DigimonFactory()
        data = {
            'name': existing_digimon.name,
            'description': 'Super cool digimon',
            'weight': 68
        }
        response = self.client.post(path=self.create_path, data=data)

        self.assertEqual(400, response.status_code)


class UpdateDigimonActionTestSuite(APITestCase):

    def setUp(self):
        self.digimon_to_update = DigimonFactory()
        self.update_path = reverse('digimon-detail', kwargs={'pk': self.digimon_to_update.pk})
        self.description_data = {'description': 'Some new description'}
        self.weight_data = {'weight': 54}

    def test_update_description_as_anonymous_user(self):
        response = self.client.patch(path=self.update_path, data=self.description_data)

        self.digimon_to_update.refresh_from_db()
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.description_data['description'], self.digimon_to_update.description)

    def test_update_description_as_authenticated_user(self):
        self.client.force_authenticate(UserFactory())
        response = self.client.patch(path=self.update_path, data=self.description_data)

        self.digimon_to_update.refresh_from_db()
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.description_data['description'], self.digimon_to_update.description)

    def test_update_weight_for_another_user_digimon(self):
        self.client.force_authenticate(UserFactory())
        response = self.client.patch(path=self.update_path, data=self.weight_data)
        print(response.data)

        self.digimon_to_update.refresh_from_db()
        self.assertEqual(403, response.status_code)
        self.assertNotEqual(self.weight_data['weight'], self.digimon_to_update.weight)

    def test_update_weight_as_digimon_creator(self):
        self.client.force_authenticate(self.digimon_to_update.creator)
        response = self.client.patch(path=self.update_path, data=self.weight_data)

        self.digimon_to_update.refresh_from_db()
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.weight_data['weight'], self.digimon_to_update.weight)

    def test_update_weight_as_anonymous_user(self):
        response = self.client.patch(path=self.update_path, data=self.weight_data)

        self.assertEqual(403, response.status_code)
        self.assertNotEqual(self.weight_data['weight'], self.digimon_to_update.weight)


class ListActionTestSuite(APITestCase):

    def setUp(self):
        self.list_path = reverse('digimon-list')
        DigimonFactory.create_batch(2)

    def test_list_as_authenticated_user(self):
        self.client.force_authenticate(UserFactory())
        response = self.client.get(self.list_path)

        self.assertEqual(200, response.status_code)
        self.assertEqual(Digimon.objects.count(), len(response.data))

    def test_list_as_anonymous_user(self):
        response = self.client.get(self.list_path)

        self.assertEqual(200, response.status_code)
        self.assertEqual(Digimon.objects.count(), len(response.data))
