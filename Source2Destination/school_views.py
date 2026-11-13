"""
School Admin Views
Source 2 Destination — Campus & Hostel Operations Portal
"""
import os
from django.shortcuts import render
from django.http import Http404
from django.template.loader import get_template
from django.template import TemplateDoesNotExist

def dashboard(request):
    """Render School Admin Primary Dashboard."""
    return render(request, 'school-admin/dashboard.html')

def render_school_page(request, path):
    """Render any School Admin subpage dynamically."""
    clean_path = os.path.normpath(path).replace('\\', '/').strip('/')
    if clean_path.startswith('..'):
        raise Http404("Invalid template path")

    candidates = [
        f"school-admin/{clean_path}",
        f"school-admin/{clean_path}.html",
    ]
    if not clean_path.endswith('.html'):
        candidates.append(f"school-admin/{clean_path}/index.html")

    for template_name in candidates:
        try:
            get_template(template_name)
            return render(request, template_name)
        except TemplateDoesNotExist:
            continue

    raise Http404(f"School Admin template '{clean_path}' not found")
