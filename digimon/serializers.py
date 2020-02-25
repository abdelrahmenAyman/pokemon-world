from rest_framework import serializers

from digimon.models import Digimon


class ReadCreateDigimonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Digimon
        fields = ('pk', 'name', 'description', 'weight')

    @staticmethod
    def validate_name(value: str) -> str:
        if Digimon.objects.filter(name=value).exists():
            raise serializers.ValidationError('Digimon with that name already exists')
        return value


class UpdateDigimonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Digimon
        fields = ('pk', 'description', 'weight')
