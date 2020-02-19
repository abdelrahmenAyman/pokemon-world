from django.contrib.auth import authenticate, login
from rest_framework import serializers


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password', 'placeholder': 'Password'},
        write_only=True)

    def validate(self, attrs):
        user = authenticate(request=self.context['request'], username=attrs['email'], password=attrs['password'])
        if user is None:
            raise serializers.ValidationError('Credentials does not match')
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
