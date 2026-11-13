"""
Franchise Partner Views
Source 2 Destination — Regional Operations Portal
"""
import os
from django.shortcuts import render
from django.http import Http404
from django.template.loader import get_template
from django.template import TemplateDoesNotExist

def dashboard(request):
    """Render Franchise Partner Dashboard."""
    return render(request, 'franchise/dashboard.html')

def render_franchise_page(request, path):
    """Render any Franchise subpage dynamically."""
    clean_path = os.path.normpath(path).replace('\\', '/').strip('/')
    if clean_path.startswith('..'):
        raise Http404("Invalid template path")

    candidates = [
        f"franchise/{clean_path}",
        f"franchise/{clean_path}.html",
    ]
    if not clean_path.endswith('.html'):
        candidates.append(f"franchise/{clean_path}/index.html")

    for template_name in candidates:
        try:
            get_template(template_name)
            return render(request, template_name)
        except TemplateDoesNotExist:
            continue

    raise Http404(f"Franchise template '{clean_path}' not found")

