import re
from django.shortcuts import redirect
from django.urls import reverse


class RoleAccessMiddleware:
    """
    Unified Institutional Authentication & Role-Based Access Control (RBAC) Middleware.
    Enforces that protected portal routes are guarded by authenticated sessions:
    - Super Admin routes (/super-admin/...) require Superuser / Global HQ privileges.
    - Franchise routes (/franchise/...) require Franchise Partner privileges.
    - School Admin routes (/school-admin/...) require School Administrator privileges.
    Unauthenticated attempts are safely redirected to the single sign-in page.
    """

    EXEMPT_PREFIXES = (
        '/static/',
        '/media/',
        '/admin/',
        '/api/',
        '/favicon.ico',
    )

    EXEMPT_EXACT = (
        '/',
        '/login/',
        '/logout/',
        '/auth/login.html',
        '/auth/logout/',
    )

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Check exemptions
        if path in self.EXEMPT_EXACT or any(path.startswith(prefix) for prefix in self.EXEMPT_PREFIXES):
            return self.get_response(request)

        # Protect portals: /super-admin/, /franchise/, /school-admin/
        is_super = path.startswith('/super-admin')
        is_franchise = path.startswith('/franchise')
        is_school = path.startswith('/school-admin')

        if is_super or is_franchise or is_school:
            if not request.user.is_authenticated:
                return redirect(f"/?next={path}")

            username = request.user.username.lower()

            # Role verification
            if is_super:
                if not (request.user.is_superuser or request.user.is_staff or username == 'admin'):
                    # Redirect non-superusers to their appropriate dashboard
                    if username == 'franchise':
                        return redirect('/franchise/dashboard.html')
                    return redirect('/school-admin/dashboard.html')

            elif is_franchise:
                if not (username == 'franchise' or request.user.is_superuser or request.user.is_staff):
                    return redirect('/school-admin/dashboard.html')

            elif is_school:
                if not (username == 'school' or request.user.is_superuser or request.user.is_staff or username == 'franchise'):
                    return redirect('/franchise/dashboard.html')

        return self.get_response(request)
