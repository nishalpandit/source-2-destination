import os
from django.shortcuts import render
from django.http import Http404
from django.template.loader import get_template
from django.template import TemplateDoesNotExist

def index(request):
    """Render root landing / sign in page."""
    return render(request, 'index.html')

def render_template_page(request, path):
    """
    Render any template dynamically by relative path,
    e.g. super-admin/dashboard.html, auth/login.html, etc.
    """
    # Prevent directory traversal
    clean_path = os.path.normpath(path).replace('\\', '/')
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
