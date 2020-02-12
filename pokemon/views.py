from typing import List, Any

from rest_framework.mixins import CreateModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import GenericViewSet

from pokemon.exceptions import PokemonDoesNotExist
from pokemon.external_pokemon_api import retrieve_pokemon_abilities
from pokemon.models import Pokemon
from pokemon.serializers import PokemonSerializer


class PokemonViewSet(GenericViewSet, CreateModelMixin, ListModelMixin, UpdateModelMixin):
    queryset = Pokemon.objects.all()
    serializer_class = PokemonSerializer

    def perform_create(self, serializer: BaseSerializer) -> None:
        abilities = retrieve_pokemon_abilities(serializer.validated_data['name'])
        serializer.save(abilities=abilities)

    def create(self, request: Request, *args: list, **kwargs: dict) -> Response:
        try:
            return super().create(request, args, kwargs)
        except PokemonDoesNotExist:
            return Response({'detail': 'That name does not match any Pokemon'}, status=400)

    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        if 'weight' in request.data and self.get_object().creator != request.user:
            return Response(status=403, data={'detail': 'Weight can only be updated by pokemon creator'})
        return super().partial_update(request, args, kwargs)

    def get_permissions(self) -> List[BasePermission]:
        if self.action == 'create':
            return [IsAuthenticated()]
        return []
