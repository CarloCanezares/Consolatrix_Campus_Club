from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import User
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse, HttpResponseBadRequest
import json
import uuid
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError

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
    """
    Accepts JSON (fetch) or regular form POST.
    Validates unique student_id and email before creating user.
    Returns JSON on fetch clients, otherwise renders template with messages.
    """
    if request.method != 'POST':
        return render(request, 'signup.html')

    # support both JSON and form POST
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body.decode('utf-8') if isinstance(request.body, (bytes, bytearray)) else request.body)
        except Exception:
            data = {}
        get = lambda k, default=None: data.get(k, default)
        is_json = True
    else:
        get = lambda k, default=None: request.POST.get(k, default)
        is_json = False

    # parse incoming values and normalize
    email = str((get('email') or '')).strip().lower()
    password = get('password') or ''
    first_name = get('firstName') or ''
    last_name = get('lastName') or ''
    raw_student_id = get('studentId') or get('student_id') or ''
    # normalize student_id to string and strip whitespace, convert to uppercase
    student_id = str(raw_student_id).strip().upper()
    year_level = get('yearLevel') or None
    department = get('department') or ''
    phone = get('phone') or ''
    bio = get('bio') or ''
    interests = get('interests') or []
    newsletter = get('newsletter') in (True, 'true', 'on', '1', 'True')

    print(f"DEBUG: Processing signup for student_id: {student_id}")

    # Basic validation
    if not email or not password:
        msg = "Email and password are required."
        if is_json:
            return JsonResponse({'success': False, 'message': msg}, status=400)
        messages.error(request, msg)
        return render(request, 'signup.html', {'email': email})

    # Enhanced student ID validation
    if not student_id:
        msg = "Student ID is required."
        if is_json:
            return JsonResponse({'success': False, 'message': msg}, status=400)
        messages.error(request, msg)
        return render(request, 'signup.html', {'email': email})

    # Validate student ID format (YYYY-XXXXX)
    import re
    student_id_pattern = re.compile(r'^\d{4}-\d{5}$')
    if not student_id_pattern.match(student_id):
        msg = "Student ID must be in format: YYYY-XXXXX (e.g., 2024-12345)"
        if is_json:
            return JsonResponse({'success': False, 'message': msg}, status=400)
        messages.error(request, msg)
        return render(request, 'signup.html', {'email': email, 'student_id': student_id})

    # Check uniqueness - use exact match since we normalized to uppercase
    try:
        if User.objects.filter(student_id=student_id).exists():
            existing_user = User.objects.get(student_id=student_id)
            msg = f"Student ID {student_id} is already registered with email: {existing_user.email}"
            print(f"DEBUG: Student ID conflict - {student_id} exists for {existing_user.email}")
            if is_json:
                return JsonResponse({'success': False, 'message': msg}, status=400)
            messages.error(request, msg)
            return render(request, 'signup.html', {'email': email, 'student_id': student_id})

        if User.objects.filter(email__iexact=email).exists():
            msg = "An account with this email already exists."
            if is_json:
                return JsonResponse({'success': False, 'message': msg}, status=400)
            messages.error(request, msg)
            return render(request, 'signup.html', {'email': email})

    except Exception as e:
        print(f"DEBUG: Error checking uniqueness: {e}")
        msg = "Error checking account availability. Please try again."
        if is_json:
            return JsonResponse({'success': False, 'message': msg}, status=400)
        messages.error(request, msg)
        return render(request, 'signup.html', {'email': email})

    # Create user
    try:
        user = User.objects.create_user(
            email=email,
            password=password,
            username=email,  # Use email as username
            first_name=first_name,
            last_name=last_name,
            student_id=student_id,  # Use the normalized student_id
        )

        # Assign optional fields
        try:
            user.year_level = int(year_level) if year_level else None
        except (ValueError, TypeError):
            user.year_level = None

        user.department = department
        user.phone = phone
        user.bio = bio
        
        # Normalize interests
        if isinstance(interests, str):
            try:
                interests = json.loads(interests)
            except Exception:
                interests = [s.strip() for s in interests.split(',') if s.strip()]
        user.interests = interests
        user.newsletter = newsletter
        
        user.save()
        print(f"DEBUG: Successfully created user: {user.email} with student_id: {user.student_id}")

    except IntegrityError as e:
        print(f"DEBUG: IntegrityError during user creation: {e}")
        # Check what specific constraint failed
        if 'student_id' in str(e).lower():
            msg = f"Student ID {student_id} is already in use. Please use a different Student ID."
        elif 'email' in str(e).lower():
            msg = "An account with this email already exists."
        else:
            msg = "Error creating account. Please try again."
        
        if is_json:
            return JsonResponse({'success': False, 'message': msg}, status=400)
        messages.error(request, msg)
        return render(request, 'signup.html', {'email': email})

    except Exception as e:
        print(f"DEBUG: Unexpected error during user creation: {e}")
        msg = "An unexpected error occurred. Please try again."
        if is_json:
            return JsonResponse({'success': False, 'message': msg}, status=400)
        messages.error(request, msg)
        return render(request, 'signup.html', {'email': email})

    # Authenticate and login
    auth_user = authenticate(request, username=email, password=password)
    if auth_user is not None:
        login(request, auth_user)
        print(f"DEBUG: Successfully authenticated and logged in user: {auth_user.email}")
    else:
        # Fallback
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        print(f"DEBUG: Used fallback login for user: {user.email}")

    if is_json:
        return JsonResponse({
            'success': True, 
            'message': 'Account created successfully',
            'redirect': '/home/'
        })
    
    messages.success(request, "Account created successfully.")
    return redirect('home')

def signout(request):
    logout(request)
    messages.success(request, "You have logged In.")
    return redirect("index")

def aboutus(request):
    return render(request, 'aboutus.html')

def events(request):
    return render(request, 'events.html')

def clubs(request):
    return render(request, 'clubs.html')

def contact(request):
    return render(request, 'contact.html')

def profile(request):
    # require login
    if not request.user.is_authenticated:
        return redirect('signin')

    user = request.user

    # try to read related clubs if your models define them
    active_clubs = []
    if hasattr(user, 'clubs'):
        try:
            active_clubs = user.clubs.all()
        except Exception:
            active_clubs = []

    context = {
        'user': user,  # Changed from 'user_obj' to 'user'
        'active_clubs': active_clubs,
    }
    return render(request, 'profile.html', context)

@login_required
@ensure_csrf_cookie
def profile_update(request):
    if request.method == 'POST':
        try:
            if request.content_type == 'application/json':
                data = json.loads(request.body.decode('utf-8') if isinstance(request.body, (bytes, bytearray)) else request.body)
            else:
                data = request.POST
            
            user = request.user
            
            # Update user fields
            full_name = data.get('fullName', '')
            if full_name:
                name_parts = full_name.split(' ', 1)
                user.first_name = name_parts[0]
                user.last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            user.phone = data.get('phone', '')
            user.bio = data.get('bio', '')
            user.department = data.get('department', '')
            
            # Update year level
            year_level = data.get('yearLevel')
            if year_level:
                try:
                    user.year_level = int(year_level)
                except:
                    pass
            
            # Update interests
            interests = data.get('interests', '')
            if isinstance(interests, str):
                user.interests = [i.strip() for i in interests.split(',') if i.strip()]
            else:
                user.interests = interests
            
            user.save()
            
            return JsonResponse({'success': True, 'message': 'Profile updated successfully'})
        
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=405)