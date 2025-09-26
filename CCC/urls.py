from django.urls import path
from . import views

urlpatterns = [
    path ('', views.index, name ='index'),
    path('sportsclub/', views.sportsclub, name='sportsclub'),
    path('artsclub/', views.artsclub, name= 'artsclub'),
    path('musicclub/', views.musicclub, name = 'musicclub'),
    path('danceclub/', views.danceclub, name= 'danceclub'),
    path('leadershipclub/', views.leadershipclub, name = 'leadershipclub'),
]