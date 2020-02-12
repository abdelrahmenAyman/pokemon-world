import random

import factory

from digimon.models import Digimon
from pokemon.factories import UserFactory


class DigimonFactory(factory.DjangoModelFactory):
    class Meta:
        model = Digimon

    name = factory.Faker('word')
    description = factory.Faker('paragraph')
    weight = round(random.uniform(1, 150), 1)
    creator = factory.SubFactory(UserFactory)
