from django.contrib.auth import get_user_model
from django.contrib.auth import logout
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from authentication.serializers import LoginSerializer, RegisterUserSerializer

User = get_user_model()


class AuthenticationViewSet(GenericViewSet):
    """Viewset was chosen to handle routing automatically so the urls are consistent"""

    @action(methods=['POST'], url_name='login', detail=False, serializer_class=LoginSerializer)
    def login(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.login_user()
        return Response(status=200, data={'detail': 'Logged in successfully'})

    @action(methods=['POST'], url_name='logout', detail=False)
    def logout(self, request: Request) -> Response:
        logout(request)
        return Response(status=200, data={'Logged out successfully'})

    @action(methods=['POST'], url_name='register', detail=False, serializer_class=RegisterUserSerializer)
    def register(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=201, data={'detail': 'User registered successfully'})
