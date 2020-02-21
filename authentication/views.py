from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from authentication.serializers import LoginSerializer

User = get_user_model()


class AuthenticationViewSet(GenericViewSet):
    """Viewset was chosen to handle routing automatically so the urls are consistent"""

    @action(methods=['POST'], url_name='login', detail=False, serializer_class=LoginSerializer)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.login_user()
        return Response()
