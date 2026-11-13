from django.urls import path, re_path
from . import views

app_name = 'source2destination'

urlpatterns = [
    path('', views.index, name='index'),
    # Exclude static/ from being captured as a template path
    re_path(r'^(?!static/)(?P<path>.+?)/?$', views.render_template_page, name='render_page'),
]
