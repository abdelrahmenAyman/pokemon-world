from typing import List, Any

from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import GenericViewSet

from digimon.models import Digimon
from digimon.serializers import DigimonSerializer


class DigimonViewSet(GenericViewSet, CreateModelMixin, UpdateModelMixin, ListModelMixin):
    serializer_class = DigimonSerializer
    permission_classes = [IsAuthenticated]
    queryset = Digimon.objects.all()

    def perform_create(self, serializer: BaseSerializer) -> None:
        serializer.save(creator=self.request.user)

    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Adds permission layer to enforce returning 403 in all cases as opposed to using custom permissions,
        which will return 401 in case of anonymous users and that is miss leading in our case.
        """
        if 'weight' in request.data and self.get_object().creator != request.user:
            return Response(status=403, data={'detail': 'Weight can only be updated by pokemon creator'})
        return super().partial_update(request, args, kwargs)

    def get_permissions(self) -> List[BasePermission]:
        if self.action == 'create':
            return [IsAuthenticated()]
        return []
