from typing import Sequence, Union

import requests
from django.db.models import QuerySet

from pokemon.exceptions import PokemonDoesNotExist
from pokemon.models import Ability, Pokemon

BASE_API_URL: str = 'https://pokeapi.co/api/v2'


def retrieve_pokemon_abilities(pokemon_name: str) -> Union[QuerySet[Ability], Sequence[Ability]]:
    """
    Retrieves pokemon based on its unique name, then extracts its abilities and returns them
    as a List of python objects.
    """
    pokemons_with_same_name = Pokemon.objects.filter(name=pokemon_name)
    if pokemons_with_same_name.exists():
        return pokemons_with_same_name[0].abilities.all()

    data = retrieve_pokemon_from_api(pokemon_name)
    return create_abilities_from_json_data(data)


def retrieve_pokemon_from_api(pokemon_name: str) -> dict:
    """Get Pokemon json data from external API"""
    pokemon_detail_path = f'{BASE_API_URL}/pokemon/{pokemon_name}/'
    response = requests.get(pokemon_detail_path)
    if response.status_code == 404:
        raise PokemonDoesNotExist
    return response.json()


def create_abilities_from_json_data(json_data: dict) -> Sequence[Ability]:
    return [create_ability_from_json(entry) for entry in json_data['abilities']]


def create_ability_from_json(ability_entry: dict) -> Ability:
    """
    Extracts ability detail url from json entry to get it from api using that url.
    Then it creates Ability object using the info returned by the api call.
    """
    ability_json = get_ability_from_api(ability_entry)
    ability_data = {
        'effect': ability_json['effect_entries'][0]['effect'],
        'short_effect': ability_json['effect_entries'][0]['short_effect'],
        'name': ability_json['name']
    }
    return Ability.objects.get_or_create(api_obj_id=ability_json['id'], defaults=ability_data)[0]


def get_ability_from_api(ability_entry: dict) -> dict:
    return requests.get(ability_entry['ability']['url']).json()
