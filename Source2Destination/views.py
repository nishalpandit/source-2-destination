import os
from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from django.template.loader import get_template
from django.template import TemplateDoesNotExist
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.models import User


def get_role_dashboard_url(user):
    """
    Determine default destination URL based on authenticated user's role:
    1. Super Admin (is_superuser / staff / admin) -> /super-admin/dashboard.html
    2. Franchise Admin (franchise) -> /franchise/dashboard.html
    3. School Admin (school) -> /school-admin/dashboard.html
    """
    username = user.username.lower() if user and user.username else ''
    if user.is_superuser or user.is_staff or username == 'admin':
        return '/super-admin/dashboard.html'
    elif username == 'franchise':
        return '/franchise/dashboard.html'
    elif username == 'school':
        return '/school-admin/dashboard.html'
    return '/school-admin/dashboard.html'


def login_view(request):
    """
    Unified Single Sign-In Portal for all roles:
    1. Super Admin (Django superuser) -> /super-admin/dashboard.html
    2. Franchise Admin (user: franchise, pass: 12345) -> /franchise/dashboard.html
    3. School Admin (user: school, pass: 12345) -> /school-admin/dashboard.html
    """
    # If user is already authenticated on GET, redirect to their role dashboard
    if request.user.is_authenticated and request.method == 'GET':
        next_url = request.GET.get('next')
        if next_url and next_url.startswith('/') and not next_url.startswith('//') and next_url != '/':
            return redirect(next_url)
        return redirect(get_role_dashboard_url(request.user))

    error = None
    login_val = ''

    if request.method == 'POST':
        login_val = (request.POST.get('username') or request.POST.get('email') or '').strip()
        password = request.POST.get('password', '')

        user = None
        if login_val and password:
            # 1. Direct authentication with provided username
            user = authenticate(request, username=login_val, password=password)

            # 2. Try email match if not authenticated and contains @
            if user is None and '@' in login_val:
                matching_user = User.objects.filter(email__iexact=login_val).first()
                if matching_user:
                    user = authenticate(request, username=matching_user.username, password=password)

            # 3. Try case-insensitive username match
            if user is None:
                matching_user = User.objects.filter(username__iexact=login_val).first()
                if matching_user:
                    user = authenticate(request, username=matching_user.username, password=password)

        if user is not None and user.is_active:
            auth_login(request, user)

            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url and next_url.startswith('/') and not next_url.startswith('//') and next_url != '/':
                dest_url = next_url
            else:
                dest_url = get_role_dashboard_url(user)

            is_ajax = (
                request.headers.get('x-requested-with') == 'XMLHttpRequest' or
                'application/json' in request.headers.get('Accept', '') or
                request.content_type == 'application/json'
            )
            if is_ajax:
                return JsonResponse({'success': True, 'redirect_url': dest_url})
            return redirect(dest_url)
        else:
            error = "Invalid username or password. Please verify your credentials."
            is_ajax = (
                request.headers.get('x-requested-with') == 'XMLHttpRequest' or
                'application/json' in request.headers.get('Accept', '') or
                request.content_type == 'application/json'
            )
            if is_ajax:
                return JsonResponse({'success': False, 'error': error}, status=400)

    context = {
        'error': error,
        'login_val': login_val,
        'next': request.GET.get('next', ''),
    }
    return render(request, 'index.html', context)


def logout_view(request):
    """Log out authenticated user and return to the unified login page."""
    auth_logout(request)
    return redirect('source2destination:login')


def index(request):
    """Entrypoint alias pointing to unified login_view."""
    return login_view(request)


def render_template_page(request, path):
    """
    Render any template dynamically by relative path,
    e.g. super-admin/dashboard.html, auth/login.html, etc.
    """
    # If legacy login requested, redirect to single login page
    clean_path = os.path.normpath(path).replace('\\', '/').strip('/')
    if clean_path in ('auth/login', 'auth/login.html', 'login', 'login.html'):
        return redirect('source2destination:login')

    if clean_path.startswith('..') or clean_path.startswith('/'):
        raise Http404("Invalid template path")

    candidates = []
    if clean_path.endswith('.html'):
        candidates.append(clean_path)
    else:
        candidates.extend([
            f"{clean_path}.html",
            f"{clean_path}/index.html",
            clean_path,
        ])

    for template_name in candidates:
        try:
            get_template(template_name)
            return render(request, template_name)
        except (TemplateDoesNotExist, PermissionError):
            continue

    raise Http404(f"Template '{clean_path}' not found")
