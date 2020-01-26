import factory

from django.contrib.auth import get_user_model
from pokemon.models import Ability

User = get_user_model()


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    username = email


class AbilityFactory(factory.DjangoModelFactory):
    class Meta:
        model = Ability

    name = factory.Faker('word')
    effect = factory.Faker('paragraph')
    short_effect = factory.Faker('paragraph')
    api_obj_id = factory.Sequence(lambda n: n)
