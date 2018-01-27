from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('artist/', views.view_artist, name='artist'),
    path('movements/', views.movements, name='movements'),
    path('vizualize/', views.vizualize, name='movements'),
    path('movements/movement/', views.view_movement, name='movement')
]
