from rest_framework import serializers

from digimon.models import Digimon


class DigimonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Digimon
        fields = ('name', 'description', 'weight')
