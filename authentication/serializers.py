from typing import Dict, Any

from django.contrib.auth import authenticate, login, get_user_model
from rest_framework import serializers

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password', 'placeholder': 'Password'},
        write_only=True)

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        user = authenticate(request=self.context['request'], username=attrs['email'], password=attrs['password'])
        if user is None:
            raise serializers.ValidationError('Credentials does not match or email does not exist')
        return attrs

    def login_user(self) -> None:
        assert hasattr(self, '_errors'), (
            'You must call `.is_valid()` before calling `.login_user()`.'
        )
        user = authenticate(
            request=self.context['request'],
            username=self.validated_data['email'],
            password=self.validated_data['password'])
        login(request=self.context['request'], user=user)


class RegisterUserSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password', 'placeholder': 'Password'},
        write_only=True)
    confirm_password = serializers.CharField(
        style={'input_type': 'password', 'placeholder': 'Password'},
        write_only=True)

    @staticmethod
    def validate_email(value: str) -> str:
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        self.validate_passwords_matching(attrs)
        return attrs

    @staticmethod
    def validate_passwords_matching(attrs: Dict[str, Any]) -> None:
        if attrs.get('password') != attrs.get('confirm_password'):
            raise serializers.ValidationError('Passwords does not match')

    def create(self, validated_data: Dict[str, Any]) -> User:
        user = User(email=validated_data.get('email'), username=validated_data.get('email'))
        user.set_password(validated_data.get('password'))
        user.save()
        return user
