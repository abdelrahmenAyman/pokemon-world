from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from authentication.views import login, logout, register
from digimon.views import DigimonViewSet
from pokemon.external_pokemon_api import get_pokemon_available_names
from pokemon.views import PokemonViewSet

settings.AVAILABLE_POKEMON_NAMES = get_pokemon_available_names()

PokemonRouter = DefaultRouter()
PokemonRouter.register('api/pokemons', PokemonViewSet, basename='pokemon')

DigimonRouter = DefaultRouter()
DigimonRouter.register('api/digimons', DigimonViewSet, basename='digimon')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(PokemonRouter.urls)),
    path('', include(DigimonRouter.urls)),
    path('api/auth/login', login, name='auth-login'),
    path('api/auth/logout', logout, name='auth-logout'),
    path('api/auth/register', register, name='auth-register'),
]
