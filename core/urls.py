from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Redirect root to the login page
    path('', RedirectView.as_view(url='/usuarios/login/', permanent=True)),
    
    # Django's built-in admin site
    path('admin/', admin.site.urls),

    # Include your app's URLs
    path('usuarios/', include('apps.usuarios.urls', namespace='usuarios')),
    # The 'tramites' app is included but has no URLs yet.
    # This makes the structure ready for future development.
    path('tramites/', include('apps.tramites.urls', namespace='tramites')),
    # URLs for tramitador functionality
    path('tramitador/', include('apps.tramites.urls_tramitador', namespace='tramitador')),
]

# --- Development Server Static and Media File Serving ---
# This is not for production use.
if settings.DEBUG:
    # This serves files uploaded by users (e.g., documents).
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
