from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticatedOrReadOnly


from pokemon.serializers import PokemonCreateSerializer
from pokemon.external_pokemon_api import retrieve_pokemon_abilities_from_api


class PokemonViewSet(GenericViewSet, CreateModelMixin):
    serializer_class = PokemonCreateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        abilities = retrieve_pokemon_abilities_from_api(serializer.validated_data['name'])
        serializer.save(abilities=abilities)
