from typing import Dict

from django.conf import settings
from rest_framework import serializers

from pokemon.models import Pokemon, Ability


class AbilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Ability
        fields = ('name', 'effect', 'short_effect', 'api_obj_id')


class ReadCreatePokemonSerializer(serializers.ModelSerializer):
    """Serializer to be used for all actions on Pokemon resource except for update actions"""
    abilities = AbilitySerializer(many=True, required=False, read_only=True)

    class Meta:
        model = Pokemon
        fields = ('pk', 'name', 'description', 'weight', 'abilities')

    @staticmethod
    def validate_name(value: str) -> str:
        if Pokemon.objects.filter(name=value).exists():
            raise serializers.ValidationError('Pokemon with that name already exists')
        if value not in settings.AVAILABLE_POKEMON_NAMES:
            raise serializers.ValidationError('That name does not match any Pokemon')
        return value

    def create(self, validated_data: Dict) -> Pokemon:
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)


class UpdatePokemonSerializer(serializers.ModelSerializer):
    weight = serializers.DecimalField(required=False, max_digits=4, decimal_places=1)

    class Meta:
        model = Pokemon
        fields = ('pk', 'description', 'weight')
