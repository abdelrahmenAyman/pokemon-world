from unittest.mock import patch, MagicMock

from requests.models import Response
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from pokemon.exceptions import PokemonDoesNotExist
from pokemon.external_pokemon_api import retrieve_pokemon_from_api, create_ability_from_json, \
    retrieve_pokemon_abilities, get_pokemon_available_names
from pokemon.factories import UserFactory, AbilityFactory, PokemonFactory
from pokemon.models import Pokemon, Ability


class CreatePokemonActionTestSuite(APITestCase):

    def setUp(self):
        self.list_path = reverse('pokemon-list')
        self.valid_creation_data = {
            'name': 'bulbasaur',
            'description': 'Mighty Pokemon',
            'weight': 59
        }

        self.logged_in_user = UserFactory()
        self.client.force_authenticate(self.logged_in_user)

    def test_user_is_not_authenticated(self):
        self.client.logout()
        response = self.client.post(path=self.list_path, data=self.valid_creation_data)
        self.assertEqual(401, response.status_code)

    @patch('pokemon.views.retrieve_pokemon_abilities')
    def test_pokemon_creator_is_set_to_request_user(self, api_call_func):
        api_call_func.return_value = [AbilityFactory() for _ in range(2)]
        response = self.client.post(path=self.list_path, data=self.valid_creation_data)
        print(response.data)

        self.assertEqual(201, response.status_code)
        self.assertEqual(self.logged_in_user, Pokemon.objects.all().first().creator)

    @patch('pokemon.views.retrieve_pokemon_abilities')
    def test_created_pokemon_has_abilities(self, api_call_func):
        api_call_func.return_value = [AbilityFactory() for _ in range(2)]
        response = self.client.post(path=self.list_path, data=self.valid_creation_data)

        self.assertEqual(201, response.status_code)
        self.assertEqual(2, Pokemon.objects.all().first().abilities.count())

    @patch('pokemon.external_pokemon_api.requests.get')
    def test_api_module_throw_exception_pokemon_does_not_Exist(self, mock_get):
        mock_response = Response()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        response = self.client.post(path=self.list_path, data=self.valid_creation_data)
        self.assertEqual(400, response.status_code)

    @patch('pokemon.views.retrieve_pokemon_abilities')
    def test_create_two_pokemons_with_same_name(self, api_call_func):
        api_call_func.return_value = [AbilityFactory() for _ in range(2)]
        pokemon = PokemonFactory()

        self.valid_creation_data['name'] = pokemon.name
        response = self.client.post(path=self.list_path, data=self.valid_creation_data)
        self.assertEqual(400, response.status_code)

    @patch('pokemon.views.retrieve_pokemon_abilities')
    def test_create_pokemon_with_invalid_name_does_not_hit_external_api(self, api_call):
        invalid_data = {
            'name': 'Non existing pokemon',
            'description': 'Mighty Pokemon',
            'weight': 59
        }
        response = self.client.post(path=self.list_path, data=invalid_data)
        self.assertEqual(400, response.status_code)
        self.assertFalse(api_call.called)


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
        self.mock_ability['id'] = duplicate_ability.api_obj_id
        api_call.return_value = self.mock_ability

        ability = create_ability_from_json(self.mock_ability_entry)
        self.assertEqual(ability.api_obj_id, duplicate_ability.api_obj_id)
        self.assertEqual(1, Ability.objects.count())

    @patch('pokemon.external_pokemon_api.retrieve_pokemon_from_api')
    def test_retrieve_pokemon_abilities_uses_db_instead_of_api_when_pokemon_with_same_name_exists(self, api_call):
        existing_pokemon = PokemonFactory(name='Great Pokemon')
        existing_abilities = [AbilityFactory() for _ in range(2)]
        for ability in existing_abilities:
            existing_pokemon.abilities.add(ability)

        abilities = retrieve_pokemon_abilities(existing_pokemon.name)

        self.assertFalse(api_call.called)
        self.assertEqual(len(existing_pokemon.abilities.all()), len(abilities))
        self.assertEqual(existing_pokemon.abilities.first().pk, abilities[0].pk)

    @patch('pokemon.external_pokemon_api.requests.get')
    def test_get_pokemon_available_names(self, api_call):
        mock_response = MagicMock()
        mock_response.json = MagicMock(return_value={
            "count": 964,
            "next": 'null',
            "previous": 'null',
            "results": [
                {
                    "name": "bulbasaur",
                    "url": "https://pokeapi.co/api/v2/pokemon/1/"
                },
                {
                    "name": "ivysaur",
                    "url": "https://pokeapi.co/api/v2/pokemon/2/"
                }, ]})
        api_call.return_value = mock_response

        result = get_pokemon_available_names()
        self.assertEqual(["bulbasaur", "ivysaur"], result)


class ListPokemonActionTestSuite(APITestCase):

    def setUp(self):
        self.list_path = reverse('pokemon-list')

    def test_list_pokemon_as_anonymous_user(self):
        PokemonFactory.create_batch(5)
        response = self.client.get(path=self.list_path)

        self.assertEqual(200, response.status_code)
        self.assertEqual(Pokemon.objects.count(), len(response.data))

    def test_list_as_authenticated_user(self):
        PokemonFactory.create_batch(5)
        self.client.force_authenticate(UserFactory())
        response = self.client.get(path=self.list_path)

        self.assertEqual(200, response.status_code)
        self.assertEqual(Pokemon.objects.count(), len(response.data))


class UpdatePokemonActionTestSuite(APITestCase):

    def setUp(self):
        self.pokemon_to_update = PokemonFactory()
        self.update_path = reverse('pokemon-detail', kwargs={'pk': self.pokemon_to_update.pk})
        self.description_data = {'description': 'Some new description'}
        self.weight_data = {'weight': 52}

    def test_update_description_as_anonymous_user(self):
        response = self.client.patch(path=self.update_path, data=self.description_data)

        self.pokemon_to_update.refresh_from_db()
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.description_data['description'], self.pokemon_to_update.description)

    def test_update_description_as_authenticated_user(self):
        self.client.force_authenticate(UserFactory())
        response = self.client.patch(path=self.update_path, data=self.description_data)

        self.pokemon_to_update.refresh_from_db()
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.description_data['description'], self.pokemon_to_update.description)

    def test_update_weight_as_pokemon_creator(self):
        self.client.force_authenticate(self.pokemon_to_update.creator)
        response = self.client.patch(path=self.update_path, data=self.weight_data)

        self.pokemon_to_update.refresh_from_db()
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.weight_data['weight'], self.pokemon_to_update.weight)

    def test_update_weight_as_anonymous_user(self):
        response = self.client.patch(path=self.update_path, data=self.weight_data)

        self.pokemon_to_update.refresh_from_db()
        self.assertEqual(403, response.status_code)
        self.assertNotEqual(self.weight_data['weight'], self.pokemon_to_update.weight)

    def test_update_another_user_pokemon_weight_as_authenticated_user(self):
        self.client.force_authenticate(UserFactory())
        response = self.client.patch(path=self.update_path, data=self.weight_data)

        self.pokemon_to_update.refresh_from_db()
        self.assertEqual(403, response.status_code)
        self.assertNotEqual(self.weight_data['weight'], self.pokemon_to_update.weight)

    def test_update_abilities(self):
        data = {'abilities': [1, 2]}
        Ability.objects.all().delete()
        self.client.patch(path=self.update_path, data=data)
        self.assertEqual(0, self.pokemon_to_update.abilities.count())
