from django.shortcuts import render
from django.http import  HttpResponse
# Create your views here.
def index(request):
    return render(request, 'index.html')

def sportsclub(request):
    return render(request, 'sportsclub.html')

def artsclub(request):
    return render(request, 'artsclub.html')

def musicclub(request):
    return render(request, 'musicclub.html')

def danceclub(request):
    return render(request, 'danceclub.html')

def leadershipclub(request):
    return render(request, 'leadershipclub.html')