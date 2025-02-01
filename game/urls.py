from django.urls import path
from . import views

urlpatterns = [
    path('', views.frontend, name='frontend'),
    path("start_game/", views.start_game, name="start_game"),
    path("play_turn/", views.play_turn, name="play_turn"),
]

