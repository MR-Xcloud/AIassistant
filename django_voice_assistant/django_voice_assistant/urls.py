"""
URL Configuration for django_voice_assistant project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    # Redirect root URL to /api/
    path('', RedirectView.as_view(url='/api/', permanent=True)),
]