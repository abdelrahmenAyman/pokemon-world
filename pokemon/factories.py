import random

import factory
from django.contrib.auth import get_user_model

from pokemon.models import Ability, Pokemon

User = get_user_model()


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    username = factory.LazyAttribute(lambda user: user.email)


class AbilityFactory(factory.DjangoModelFactory):
    class Meta:
        model = Ability

    name = factory.Faker('word')
    effect = factory.Faker('paragraph')
    short_effect = factory.Faker('paragraph')
    api_obj_id = factory.Sequence(lambda n: n)


class PokemonFactory(factory.DjangoModelFactory):
    class Meta:
        model = Pokemon

    name = factory.Faker('word')
    description = factory.Faker('paragraph')
    weight = round(random.uniform(1, 150), 1)
    creator = factory.SubFactory(UserFactory)

    @factory.post_generation
    def abilities(self, create, extracted, **kwargs):
        if not create:
            # Simple Build, do nothing.
            return
        if extracted:
            # A list of abilities were passed in
            for ability in extracted:
                self.abilities.add(ability)
