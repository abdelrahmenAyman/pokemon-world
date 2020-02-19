from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from auth.views import AuthenticationViewSet
from digimon.views import DigimonViewSet
from pokemon.external_pokemon_api import get_pokemon_available_names
from pokemon.views import PokemonViewSet

settings.AVAILABLE_POKEMON_NAMES = get_pokemon_available_names()

PokemonRouter = DefaultRouter()
PokemonRouter.register('pokemons', PokemonViewSet, basename='pokemon')

DigimonRouter = DefaultRouter()
DigimonRouter.register('digimons', DigimonViewSet, basename='digimon')

AuthenticationRouter = DefaultRouter()
AuthenticationRouter.register('auth', AuthenticationViewSet, basename='auth')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(PokemonRouter.urls)),
    path('', include(DigimonRouter.urls)),
    path('', include(AuthenticationRouter.urls))
]
