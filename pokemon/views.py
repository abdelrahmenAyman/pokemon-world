from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from pokemon.exceptions import PokemonDoesNotExist
from pokemon.serializers import PokemonCreateSerializer
from pokemon.external_pokemon_api import retrieve_pokemon_abilities


class PokemonViewSet(GenericViewSet, CreateModelMixin):
    serializer_class = PokemonCreateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        abilities = retrieve_pokemon_abilities(serializer.validated_data['name'])
        serializer.save(abilities=abilities)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, args, kwargs)
        except PokemonDoesNotExist:
            return Response({'detail': 'That name does not match any Pokemon'}, status=400)
