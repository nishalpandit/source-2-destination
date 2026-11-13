"""
URL configuration for project project.
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

urlpatterns = [
    path('admin/', admin.site.urls),
]

# Serve static files in development
urlpatterns += staticfiles_urlpatterns()

# Application routes
urlpatterns += [
    path('', include('Source2Destination.urls')),
]
