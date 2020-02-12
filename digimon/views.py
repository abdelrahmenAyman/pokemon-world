from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.serializers import BaseSerializer
from rest_framework.viewsets import GenericViewSet

from digimon.serializers import DigimonSerializer


class DigimonViewSet(GenericViewSet, CreateModelMixin):
    serializer_class = DigimonSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer: BaseSerializer) -> None:
        serializer.save(creator=self.request.user)
