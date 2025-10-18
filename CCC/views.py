from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from django.utils import timezone
from django.db.models import Count
from .models import Club, ClubApplication, User  # Import models instead of defining them
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
import json
from django.contrib.auth import get_user_model, update_session_auth_hash

User = get_user_model()

def trial(request):
    return render(request, 'trial.html')

def index(request):
    return render(request, 'index.html')

def settings(request):
    return render(request, 'settings.html')

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
    if request.method != 'POST':
        return render(request, 'signup.html')

    # Handle both JSON and form data
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data'}, status=400)
    else:
        data = request.POST

    email = data.get('email', '').strip()
    password = data.get('password', '')
    first_name = data.get('firstName', '')
    last_name = data.get('lastName', '')
    student_id = data.get('studentId', '')

    # Basic validation
    if not email or not password:
        return JsonResponse({
            'success': False,
            'message': 'Email and password are required.'
        }, status=400)

    try:
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'message': 'An account with this email already exists.'
            }, status=400)

        # Create new user
        user = User.objects.create_user(
            email=email,
            password=password,
            username=email,  # Use email as username
            first_name=first_name,
            last_name=last_name,
            student_id=student_id
        )

        # Log the user in
        login(request, authenticate(request, username=email, password=password))

        return JsonResponse({
            'success': True,
            'message': 'Account created successfully!',
            'redirect': '/home/'
        })

    except Exception as e:
        print(f"Registration error: {str(e)}")  # For debugging
        return JsonResponse({
            'success': False,
            'message': f'Error creating account: {str(e)}'
        }, status=500)

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

@login_required
@require_http_methods(["POST"])
def apply_club(request, club_slug=None):
    """
    Accepts the existing form (unchanged). Creates the Club if missing,
    creates a ClubApplication and returns JSON for the current frontend alert.
    Works when URL provides club_slug or when the form sends 'club_type' or 'club_slug'.
    """
    # determine slug/name from URL or form fields (support legacy forms)
    form_slug = request.POST.get('club_slug') or request.POST.get('club_type') or request.POST.get('club')
    source = club_slug or form_slug or ''
    source = str(source).strip()
    if not source:
        return JsonResponse({'success': False, 'message': 'No club specified.'}, status=400)

    # normalize slug and pretty name
    raw = source.lower().replace(' ', '-')
    slug = slugify(raw)
    if slug.endswith('-club'):
        pretty = source.replace('-', ' ').title()
    else:
        pretty = (source.replace('-', ' ').title())
    try:
        club, created = Club.objects.get_or_create(
            slug=slug,
            defaults={'name': pretty if pretty else slug.title() + ' Club' }
        )

        # prevent duplicate pending or approved applications
        exists = ClubApplication.objects.filter(user=request.user, club=club).exclude(status=ClubApplication.STATUS_REJECTED).exists()
        if exists:
            return JsonResponse({
                'success': False,
                'message': f'You already have an active application or membership for {club.name}.'
            })

        # create application using any message/fields submitted by the form
        message = request.POST.get('message', '') or request.POST.get('content', '')
        app = ClubApplication.objects.create(
            user=request.user,
            club=club,
            message=message,
            status=ClubApplication.STATUS_PENDING
        )

        return JsonResponse({
            'success': True,
            'message': f'Application submitted succesfuly for {club.name}.\nwe\'ll review your application and contact you within 3-5 business days. check your email for updates.'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error submitting application: {str(e)}'}, status=500)


@login_required
def profile(request):
    """
    Provide profile context expected by templates:
    - active_clubs: clubs where user is a member
    - pending_applications: user's pending applications
    - approved_applications / rejected_applications for display
    """
    user = request.user
    active_clubs = user.clubs.all()  # uses ManyToMany related_name='clubs'
    all_apps = ClubApplication.objects.filter(user=user).select_related('club').order_by('-created_at')
    context = {
        'user': user,
        'active_clubs': active_clubs,
        'pending_applications': all_apps.filter(status=ClubApplication.STATUS_PENDING),
        'approved_applications': all_apps.filter(status=ClubApplication.STATUS_APPROVED),
        'rejected_applications': all_apps.filter(status=ClubApplication.STATUS_REJECTED),
    }
    return render(request, 'profile.html', context)


@login_required
@require_http_methods(["POST"])
def profile_update(request):
    """
    Accepts POST from profile form. Updates fields when present on user model.
    Returns JSON on AJAX/fetch, otherwise redirects back to profile.
    """
    user = request.user
    data = request.POST

    # Full name -> first_name / last_name
    full_name = data.get('fullName') or data.get('full_name') or ''
    if full_name:
        parts = full_name.strip().split(None, 1)
        user.first_name = parts[0]
        user.last_name = parts[1] if len(parts) > 1 else ''

    # Common fields
    email = data.get('email')
    if email:
        user.email = email

    if hasattr(user, 'phone'):
        phone = data.get('phone')
        if phone is not None:
            user.phone = phone

    if hasattr(user, 'year_level'):
        year_level = data.get('yearLevel') or data.get('year_level')
        if year_level is not None:
            user.year_level = year_level

    if hasattr(user, 'department'):
        dept = data.get('department')
        if dept is not None:
            user.department = dept

    if hasattr(user, 'bio'):
        bio = data.get('bio')
        if bio is not None:
            user.bio = bio

    # interests: split comma list into python list when provided
    if hasattr(user, 'interests'):
        interests_raw = data.get('interests')
        if interests_raw is not None:
            # convert "a, b, c" -> ["a","b","c"]
            interests_list = [s.strip() for s in interests_raw.split(',') if s.strip()]
            try:
                user.interests = interests_list
            except Exception:
                # fallback to raw string if assignment fails
                user.interests = interests_raw

    try:
        user.save()
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error saving profile: {str(e)}'}, status=500)

    # respond JSON for fetch; otherwise redirect
    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json':
        return JsonResponse({'success': True, 'message': 'Profile updated successfully'})
    messages.success(request, 'Profile updated successfully')
    return redirect('profile')

@login_required
@require_http_methods(["POST"])
def leave_club(request, club_id):
    """
    Allow a user to leave a club (remove self from club.members).
    Accepts POST only. Returns JSON.
    """
    club = get_object_or_404(Club, pk=club_id)
    if request.user in club.members.all():
        club.members.remove(request.user)
        return JsonResponse({'success': True, 'message': 'You have left the club.'})
    return JsonResponse({'success': False, 'message': 'You are not a member of this club.'}, status=400)


@staff_member_required
def admin_dashboard(request):
    """Admin dashboard view with statistics"""
    context = {
        'total_applications': ClubApplication.objects.count(),
        'pending_applications': ClubApplication.objects.filter(status='PENDING').count(),
        'total_clubs': Club.objects.count(),
        'total_members': Club.objects.aggregate(total=Count('members'))['total'] or 0,
        'recent_applications': ClubApplication.objects.select_related('user', 'club').order_by('-created_at')[:10]
    }
    return render(request, 'admin_dashboard.html', context)

@staff_member_required
def club_applications_list(request):
    """Staff view for managing applications"""
    applications = ClubApplication.objects.select_related('user', 'club').order_by('-created_at')
    context = {
        'applications': applications,
        'pending_count': applications.filter(status='PENDING').count()
    }
    return render(request, 'admin_applications.html', context)

@staff_member_required
@require_http_methods(["POST"])
def application_action(request, pk, action):
    """
    Approve or reject an application (called from staff UI).
    Expects POST. Returns JSON with updated status.
    """
    app = get_object_or_404(ClubApplication, pk=pk)
    if action not in ('approve', 'reject'):
        return JsonResponse({'success': False, 'message': 'Invalid action'}, status=400)

    if action == 'approve':
        if app.status != ClubApplication.STATUS_APPROVED:
            app.status = ClubApplication.STATUS_APPROVED
            app.reviewed_at = timezone.now()
            app.reviewer = request.user
            app.save()
            app.club.members.add(app.user)
    else:
        if app.status != ClubApplication.STATUS_REJECTED:
            app.status = ClubApplication.STATUS_REJECTED
            app.reviewed_at = timezone.now()
            app.reviewer = request.user
            app.save()

    return JsonResponse({'success': True, 'status': app.status, 'application_id': app.id})

@staff_member_required
@require_http_methods(["POST"])
def delete_club(request, club_id):
    """
    Allow staff/admin to delete a club. Accepts POST only.
    """
    club = get_object_or_404(Club, pk=club_id)
    name = club.name
    club.delete()
    return JsonResponse({'success': True, 'message': f'Club "{name}" deleted.'})

@login_required
@require_http_methods(["POST"])
def settings_update_general(request):
    """
    Accepts JSON body { displayName, email, phone } or form POST.
    Returns JSON.
    """
    try:
        payload = json.loads(request.body.decode()) if request.body else request.POST
    except Exception:
        payload = request.POST

    user = request.user
    display_name = payload.get('displayName') or payload.get('display_name')
    email = payload.get('email')
    phone = payload.get('phone')

    if display_name:
        parts = display_name.strip().split(None, 1)
        user.first_name = parts[0]
        user.last_name = parts[1] if len(parts) > 1 else ''

    if email:
        # prevent duplicate email
        if User.objects.filter(email=email).exclude(pk=user.pk).exists():
            return JsonResponse({'success': False, 'message': 'Email already in use.'}, status=400)
        user.email = email

    if hasattr(user, 'phone'):
        user.phone = phone or getattr(user, 'phone', '')

    try:
        user.save()
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error saving: {str(e)}'}, status=500)

    return JsonResponse({'success': True, 'message': 'Settings saved successfully'})

@login_required
@require_http_methods(["POST"])
def settings_update_password(request):
    """
    Accepts JSON body { currentPassword, newPassword } or form POST.
    Returns JSON and keeps user logged in.
    """
    try:
        payload = json.loads(request.body.decode()) if request.body else request.POST
    except Exception:
        payload = request.POST

    current = payload.get('currentPassword')
    new_password = payload.get('newPassword')

    if not current or not new_password:
        return JsonResponse({'success': False, 'message': 'Missing current or new password.'}, status=400)

    user = request.user
    if not user.check_password(current):
        return JsonResponse({'success': False, 'message': 'Current password is incorrect.'}, status=400)

    if len(new_password) < 8:
        return JsonResponse({'success': False, 'message': 'New password must be at least 8 characters.'}, status=400)

    try:
        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)  # keep user logged in
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Error updating password: {str(e)}'}, status=500)

    return JsonResponse({'success': True, 'message': 'Password updated successfully'})