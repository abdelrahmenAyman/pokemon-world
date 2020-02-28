from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from rest_framework.routers import DefaultRouter

from authentication.views import login, logout, register
from digimon.views import DigimonViewSet
from pokemon.external_pokemon_api import get_pokemon_available_names
from pokemon.views import PokemonViewSet

settings.AVAILABLE_POKEMON_NAMES = get_pokemon_available_names()

schema_view = get_schema_view(
    openapi.Info(
        title="Pokemon World API",
        default_version='v1',
        description="API for sharing pokemons and digimons",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

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
    path('api/docs', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
