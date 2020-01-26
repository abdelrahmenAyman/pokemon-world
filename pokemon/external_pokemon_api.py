import requests
from typing import List, Dict

from pokemon.exceptions import PokemonDoesNotExist
from pokemon.models import Ability


def retrieve_pokemon_abilities_from_api(pokemon_name: str) -> List[Ability]:
    """
    Retrieves pokemon based on its unique name, then extracts its abilities and returns them
    as a List of python objects.
    """

    data = retrieve_pokemon_from_api(pokemon_name)
    return create_abilities_from_json_data(data)


def retrieve_pokemon_from_api(pokemon_name: str) -> Dict:
    pokemon_detail_path = f'https://pokeapi.co/api/v2/pokemon/{pokemon_name}/'
    response = requests.get(pokemon_detail_path)
    if response.status_code == 404:
        raise PokemonDoesNotExist
    return response.json()


def create_abilities_from_json_data(json_data: Dict) -> List[Ability]:
    return [create_ability_from_json(entry) for entry in json_data['abilities']]


def create_ability_from_json(ability_entry: Dict) -> Ability:
    """
    Extracts ability detail url from json entry to get it from api using that url.
    Then it creates Ability object using the info returned by the api call.
    """
    ability = get_ability_from_api(ability_entry)
    ability_data = {
        'effect': ability['effect_entries'][0]['effect'],
        'short_effect': ability['effect_entries'][0]['short_effect'],
        'name': ability['name']
    }
    ability, _ = Ability.objects.get_or_create(api_obj_id=ability['id'], defaults=ability_data)
    return ability


def get_ability_from_api(ability_entry):
    return requests.get(ability_entry['ability']['url']).json()
