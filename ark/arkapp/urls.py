from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('artist/', views.view_artist, name='artist'),
    path('artworks/', views.view_artworks, name='artworks'),
    path('artwork/', views.view_artwork, name='artwork'),
    path('movements/', views.movements, name='movements'),
    path('visualize/', views.visualize, name='movements'),
    path('movements/movement/', views.view_movement, name='movement')
]
