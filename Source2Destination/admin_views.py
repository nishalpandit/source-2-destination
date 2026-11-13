"""
Super Admin Environment Views
Source 2 Destination — Global Governance Portal
"""
import os
from django.shortcuts import render
from django.http import Http404
from django.template.loader import get_template
from django.template import TemplateDoesNotExist

def dashboard(request):
    """Render Super Admin Primary Dashboard."""
    return render(request, 'super-admin/dashboard.html')

def render_admin_page(request, path):
    """Render any Super Admin subpage dynamically."""
    clean_path = os.path.normpath(path).replace('\\', '/').strip('/')
    if clean_path.startswith('..'):
        raise Http404("Invalid template path")

    candidates = [
        f"super-admin/{clean_path}",
        f"super-admin/{clean_path}.html",
    ]
    if not clean_path.endswith('.html'):
        candidates.append(f"super-admin/{clean_path}/index.html")

    for template_name in candidates:
        try:
            get_template(template_name)
            return render(request, template_name)
        except TemplateDoesNotExist:
            continue

    raise Http404(f"Super Admin template '{clean_path}' not found")
