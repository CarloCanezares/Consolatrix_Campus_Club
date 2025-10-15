from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('sportsclub/', views.sportsclub, name='sportsclub'),
    path('artsclub/', views.artsclub, name='artsclub'),
    path('musicclub/', views.musicclub, name='musicclub'),
    path('danceclub/', views.danceclub, name='danceclub'),
    path('leadershipclub/', views.leadershipclub, name='leadershipclub'),
    path('readingclub/', views.readingclub, name='readingclub'),
    path('home/', views.home, name='home'),
    path('signin/', views.signin, name='signin'),
    path('signup/', views.signup, name='signup'),
    path('signout/', views.signout, name='signout'),  # Use this one
    path('aboutus/', views.aboutus, name='aboutus'),
    path('events/', views.events, name='events'),
    path('clubs/', views.clubs, name='clubs'),
    path('contact/', views.contact, name='contact'),
    path('profile/', views.profile, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('settings/', views.settings, name='settings'),  # New settings path
    path('trial/', views.trial, name='trial'),  # New trial path
]