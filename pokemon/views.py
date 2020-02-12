from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import GenericViewSet

from pokemon.exceptions import PokemonDoesNotExist
from pokemon.external_pokemon_api import retrieve_pokemon_abilities
from pokemon.serializers import PokemonCreateSerializer


class PokemonViewSet(GenericViewSet, CreateModelMixin):
    serializer_class = PokemonCreateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer: BaseSerializer) -> None:
        abilities = retrieve_pokemon_abilities(serializer.validated_data['name'])
        serializer.save(abilities=abilities)

    def create(self, request: Request, *args: list, **kwargs: dict) -> Response:
        try:
            return super().create(request, args, kwargs)
        except PokemonDoesNotExist:
            return Response({'detail': 'That name does not match any Pokemon'}, status=400)
