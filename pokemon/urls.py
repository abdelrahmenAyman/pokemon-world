from django.contrib import admin
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from pokemon.views import PokemonViewSet


PokemonRouter = DefaultRouter()
PokemonRouter.register('pokemons', PokemonViewSet, basename='pokemon')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(PokemonRouter.urls))
]
