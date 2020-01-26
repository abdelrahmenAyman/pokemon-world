from unittest.mock import patch
from requests.models import Response

from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from pokemon.exceptions import PokemonDoesNotExist
from pokemon.factories import UserFactory, AbilityFactory
from pokemon.models import Pokemon, Ability
from pokemon.external_pokemon_api import retrieve_pokemon_from_api, create_ability_from_json


class CreatePokemonActionTestSuite(APITestCase):

    def setUp(self):
        self.list_path = reverse('pokemon-list')
        self.valid_creation_data = {
            'name': 'bulbasaur',
            'description': 'Mighty Pokemon',
            'weight': 59
        }

        self.logged_in_user = UserFactory()
        self.client.force_login(self.logged_in_user)

    @patch('pokemon.views.retrieve_pokemon_abilities_from_api')
    def test_pokemon_creator_is_set_to_request_user(self, api_call_func):
        api_call_func.return_value = [AbilityFactory() for _ in range(2)]
        response = self.client.post(path=self.list_path, data=self.valid_creation_data)

        self.assertEqual(201, response.status_code)
        self.assertEqual(self.logged_in_user, Pokemon.objects.all().first().creator)

    @patch('pokemon.views.retrieve_pokemon_abilities_from_api')
    def test_created_pokemon_has_abilities(self, api_call_func):
        api_call_func.return_value = [AbilityFactory() for _ in range(2)]
        response = self.client.post(path=self.list_path, data=self.valid_creation_data)

        self.assertEqual(201, response.status_code)
        self.assertEqual(2, Pokemon.objects.all().first().abilities.count())


class ExternalPokemonAPIModuleTestSuite(APITestCase):

    def setUp(self):
        self.mock_ability = {
            'effect_entries': [
                {
                    'effect': 'Ability Effect',
                    'short_effect': 'Ability Short Effect'
                }
            ],
            'name': 'Super Ability',
            'id': 0
        }
        self.mock_ability_entry = {
            'ability': {
                'url': '/some/path'
            }
        }

    @patch('pokemon.external_pokemon_api.requests.get')
    def test_get_pokemon_from_api_using_invalid_pokemon_name(self, mock_get):
        mock_response = Response()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        self.assertRaises(PokemonDoesNotExist, retrieve_pokemon_from_api, 'invalid pokemon name')

    @patch('pokemon.external_pokemon_api.get_ability_from_api')
    def test_create_ability_from_json_creates_ability_object_in_db(self, api_call):
        api_call.return_value = self.mock_ability
        ability = create_ability_from_json(self.mock_ability_entry)
        self.assertEqual(1, Ability.objects.count())
        self.assertEqual(self.mock_ability['effect_entries'][0]['effect'], ability.effect)
        self.assertEqual(self.mock_ability['effect_entries'][0]['short_effect'], ability.short_effect)
        self.assertEqual(self.mock_ability['name'], ability.name)
        self.assertEqual(self.mock_ability['id'], ability.api_obj_id)

    @patch('pokemon.external_pokemon_api.get_ability_from_api')
    def test_create_ability_from_json_does_not_create_duplicates(self, api_call):
        duplicate_ability = AbilityFactory()
        api_call.return_value = self.mock_ability

        ability = create_ability_from_json(self.mock_ability_entry)
        self.assertEqual(ability.api_obj_id, duplicate_ability.api_obj_id)
        self.assertEqual(1, Ability.objects.count())
