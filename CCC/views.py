from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse, HttpResponseBadRequest
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password

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

def readingclub(request):
    return render(request, 'readingclub.html')

@login_required
def home(request):
    return render(request, 'home.html')

@ensure_csrf_cookie
def signin(request):
    if request.method == "POST":
        email = request.POST.get("email") or (json.loads(request.body).get("email") if request.content_type == "application/json" else None)
        password = request.POST.get("password") or (json.loads(request.body).get("password") if request.content_type == "application/json" else None)
        next_url = request.GET.get('next') or request.POST.get('next') or 'home'

        print(f"Attempting login with email: {email}")  # Debug
        if not email or not password:
            messages.error(request, "Email and password are required.")
            return render(request, "signin.html", {"email": email or ""})

        user = authenticate(request, username=email, password=password)
        print(f"Authentication result: {user}")
        if user is not None:
            login(request, user)
            # JSON client
            if request.content_type == "application/json":
                return JsonResponse({"success": True, "redirect": next_url})
            return redirect(next_url)
        else:
            messages.error(request, "Invalid email or password.")
            return render(request, "signin.html", {"email": email or ""})

    return render(request, "signin.html")


@ensure_csrf_cookie
def signup(request):
    if request.method == 'POST':
        try:
            # accept JSON or form POST
            if request.content_type == "application/json":
                data = json.loads(request.body)
                get = lambda k, default=None: data.get(k, default)
            else:
                get = lambda k, default=None: request.POST.get(k, default)

            email = get('email')
            password = get('password')
            first_name = get('firstName') or get('first_name') or ''
            last_name = get('lastName') or get('last_name') or ''
            student_id = get('studentId') or get('student_id') or ''
            year_level = get('yearLevel') or get('year_level') or None
            phone = get('phone') or ''
            bio = get('bio') or ''
            interests = get('interests') or []
            newsletter = get('newsletter') in (True, 'true', 'on', '1', 'True')

            if not email or not password:
                raise ValueError("Email and password are required")

            # create user with manager
            user = User.objects.create_user(
                email=email,
                password=password,
                username=email,  # ensure username set (your manager sets this too)
                first_name=first_name,
                last_name=last_name,
            )
            # set extra fields if present
            if student_id:
                user.student_id = student_id
            if year_level:
                try:
                    user.year_level = int(year_level)
                except Exception:
                    user.year_level = None
            user.phone = phone
            user.bio = bio
            # interests may be list or comma string
            if isinstance(interests, str):
                try:
                    interests = json.loads(interests)
                except Exception:
                    interests = [s.strip() for s in interests.split(',') if s.strip()]
            user.interests = interests
            user.newsletter = newsletter
            user.save()

            login(request, user)
            if request.content_type == "application/json":
                return JsonResponse({"success": True, "message": "Account created", "redirect": "/home/"})
            messages.success(request, "Account created successfully.")
            return redirect('home')

        except Exception as e:
            err = str(e)
            if request.content_type == "application/json":
                return JsonResponse({"success": False, "message": f"Error creating account: {err}"}, status=400)
            messages.error(request, f"Error creating account: {err}")
            return render(request, 'signup.html')

    return render(request, 'signup.html')

def signout(request):
    logout(request)
    messages.success(request, "You have logged out.")
    return redirect("index")

def aboutus(request):
    return render(request, 'aboutus.html')

def events(request):
    return render(request, 'events.html')

def clubs(request):
    return render(request, 'clubs.html')

def contact(request):
    return render(request, 'contact.html')