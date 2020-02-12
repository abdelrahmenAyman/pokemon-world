from typing import Dict

from rest_framework import serializers

from pokemon.models import Pokemon


class PokemonCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pokemon
        fields = ('name', 'description', 'weight')

    @staticmethod
    def validate_name(value: str) -> str:
        if Pokemon.objects.filter(name=value).exists():
            raise serializers.ValidationError('Pokemon with that name already exists')
        return value

    def create(self, validated_data: Dict) -> Pokemon:
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)
