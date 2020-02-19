from django.contrib.auth import authenticate
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

    def login_user(self):
        pass
