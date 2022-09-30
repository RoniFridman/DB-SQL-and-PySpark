from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add_pokemon', views.add_pokemon, name='add_pokemon'),
    path('query_results', views.query_results, name='query_results'),
]