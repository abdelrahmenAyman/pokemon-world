from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Ability(models.Model):
    """
    Represents a Pokemon ability.
    api_obj_id is the ability id in the external api, included to help avoid creating several objects for the same
    ability.
    """
    name = models.CharField(max_length=75)
    effect = models.CharField(max_length=300)
    short_effect = models.CharField(max_length=150)
    api_obj_id = models.IntegerField(primary_key=True)


class Pokemon(models.Model):
    name = models.CharField(max_length=75)
    description = models.CharField(max_length=250)
    weight = models.DecimalField(max_digits=4, decimal_places=1)
    abilities = models.ManyToManyField(Ability, related_name='pokemons')
    creator = models.ForeignKey(User, related_name='created_pokemons', on_delete=models.SET_NULL, null=True)
