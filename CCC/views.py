from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse, HttpResponseBadRequest
import json
import uuid
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
        # support both application/json (fetch) and regular form POST
        if request.content_type == "application/json":
            try:
                payload = json.loads(request.body.decode('utf-8') if isinstance(request.body, (bytes, bytearray)) else request.body)
            except Exception:
                payload = {}
            email = payload.get("email")
            password = payload.get("password")
        else:
            email = request.POST.get("email")
            password = request.POST.get("password")

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return render(request, "signin.html", {"email": email or ""})

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            # redirect to next or home
            next_url = request.GET.get("next") or request.POST.get("next") or "home"
            # if client expects JSON respond accordingly
            if request.content_type == "application/json":
                return JsonResponse({"success": True, "redirect": next_url})
            return redirect(next_url)

        messages.error(request, "Invalid email or password.")
        return render(request, "signin.html", {"email": email or ""})

    return render(request, "signin.html")


@ensure_csrf_cookie
def signup(request):
    if request.method == 'POST':
        try:
            # accept JSON or form POST
            if request.content_type == 'application/json':
                data = json.loads(request.body.decode('utf-8') if isinstance(request.body, (bytes, bytearray)) else request.body)
                get = lambda k, default=None: data.get(k, default)
            else:
                get = lambda k, default=None: request.POST.get(k, default)

            email = get('email')
            password = get('password')
            first_name = get('firstName') or get('first_name') or ''
            last_name = get('lastName') or get('last_name') or ''
            student_id = (get('studentId') or get('student_id') or '').strip()
            year_level = get('yearLevel') or get('year_level') or None
            phone = get('phone') or ''
            bio = get('bio') or ''
            interests = get('interests') or []
            newsletter = get('newsletter') in (True, 'true', 'on', '1', 'True')

            if not email or not password:
                raise ValueError("Email and password are required")

            # If student_id provided, ensure unique
            if student_id:
                if User.objects.filter(student_id=student_id).exists():
                    msg = "Student ID already in use. Please use a different Student ID."
                    if request.content_type == 'application/json':
                        return JsonResponse({'success': False, 'message': msg}, status=400)
                    messages.error(request, msg)
                    return render(request, 'signup.html', {'email': email, 'student_id': student_id})

            # Create user
            user = User.objects.create_user(
                email=email,
                password=password,
                username=email,
                first_name=first_name,
                last_name=last_name,
            )

            # If no student_id provided, generate a short unique one
            if not student_id:
                candidate = uuid.uuid4().hex[:8]
                while User.objects.filter(student_id=candidate).exists():
                    candidate = uuid.uuid4().hex[:8]
                user.student_id = candidate
            else:
                user.student_id = student_id

            # optional fields
            try:
                user.year_level = int(year_level) if year_level else None
            except Exception:
                user.year_level = None

            user.phone = phone
            user.bio = bio

            # normalize interests
            if isinstance(interests, str):
                try:
                    interests = json.loads(interests)
                except Exception:
                    interests = [s.strip() for s in interests.split(',') if s.strip()]
            user.interests = interests
            user.newsletter = newsletter
            user.save()

            # Authenticate to ensure backend is set (preferred)
            auth_user = authenticate(request, username=email, password=password)
            if auth_user is not None:
                login(request, auth_user)
            else:
                # Fallback: set backend explicitly when authenticate didn't return a user
                # (use the import path of your custom backend)
                user.backend = 'CCC.auth.EmailBackend'
                login(request, user)

            if request.content_type == 'application/json':
                return JsonResponse({'success': True, 'message': 'Account created', 'redirect': '/home/'})
            messages.success(request, "Account created successfully.")
            return redirect('home')

        except Exception as e:
            err = str(e)
            if request.content_type == 'application/json':
                return JsonResponse({'success': False, 'message': f'Error creating account: {err}'}, status=400)
            messages.error(request, f'Error creating account: {err}')
            return render(request, 'signup.html', {'email': email or ''})

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