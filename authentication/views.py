from django.contrib import auth
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from authentication.serializers import LoginSerializer, RegisterUserSerializer

User = auth.get_user_model()


@api_view(['POST'])
def login(request: Request) -> Response:
    serializer = LoginSerializer(data=request.data, context={'request': request})
    serializer.is_valid(raise_exception=True)
    serializer.login_user()
    return Response(status=200, data={'Logged in successfully'})


@api_view(['POST'])
def logout(request: Request) -> Response:
    auth.logout(request)
    return Response(status=200, data={'Logged out successfully'})


@api_view(['POST'])
def register(request: Request) -> Response:
    serializer = RegisterUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(status=201, data={'User registered successfully'})
