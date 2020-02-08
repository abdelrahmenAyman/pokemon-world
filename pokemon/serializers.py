from rest_framework import serializers

from pokemon.models import Pokemon


class PokemonCreateSerializer(serializers.ModelSerializer):
    """
    Serializer intended to be used with create action in PokemonViewSet
    """

    class Meta:
        model = Pokemon
        fields = ('name', 'description', 'weight')

    def validate_name(self, value):
        if Pokemon.objects.filter(name=value).exists():
            raise serializers.ValidationError('Pokemon with that name already exists')
        return value

    def create(self, validated_data):
        validated_data['creator'] = self.context['request'].user
        return super().create(validated_data)
