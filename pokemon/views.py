from typing import List, Any, Dict, Type

from django.conf import settings
from rest_framework.metadata import SimpleMetadata
from rest_framework.mixins import CreateModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import GenericViewSet

from pokemon.exceptions import PokemonDoesNotExist
from pokemon.external_pokemon_api import retrieve_pokemon_abilities
from pokemon.models import Pokemon
from pokemon.serializers import ReadCreatePokemonSerializer, UpdatePokemonSerializer


class PokemonViewSetMetaData(SimpleMetadata):
    """The purpose of this class is to provide name options for the options request"""

    def get_serializer_info(self, serializer: BaseSerializer) -> Dict[str, Dict[str, Any]]:
        info = super().get_serializer_info(serializer)
        info['name']['choices'] = settings.AVAILABLE_POKEMON_NAMES
        return info


class PokemonViewSet(GenericViewSet, CreateModelMixin, ListModelMixin, UpdateModelMixin):
    queryset = Pokemon.objects.all()
    serializer_class = ReadCreatePokemonSerializer
    metadata_class = PokemonViewSetMetaData

    def perform_create(self, serializer: BaseSerializer) -> None:
        abilities = retrieve_pokemon_abilities(serializer.validated_data['name'])
        serializer.save(abilities=abilities)

    def create(self, request: Request, *args: list, **kwargs: dict) -> Response:
        try:
            return super().create(request, args, kwargs)
        except PokemonDoesNotExist:
            return Response({'detail': 'That name does not match any Pokemon'}, status=400)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Adds permission layer to enforce returning 403 in all cases as opposed to using custom permissions,
        which will return 401 in case of anonymous users and that is miss leading in our case.
        """
        if 'weight' in request.data and self.get_object().creator != request.user:
            return Response(status=403, data={'detail': 'Weight can only be updated by pokemon creator'})
        return super().update(request, *args, **kwargs)

    def get_permissions(self) -> List[BasePermission]:
        if self.action == 'create':
            return [IsAuthenticated()]
        return []

    def get_serializer_class(self) -> Type[BaseSerializer]:
        if self.action in ['partial_update', 'update']:
            return UpdatePokemonSerializer
        return ReadCreatePokemonSerializer
