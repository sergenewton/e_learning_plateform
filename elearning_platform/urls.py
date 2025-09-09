"""
URL configuration for elearning_platform project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from courses.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('accounts/', include('accounts.urls')),
    path('courses/', include('courses.urls', namespace='courses')),
    path('quizzes/', include('quizzes.urls')),
    path('certificates/', include('certificates.urls')),
]

# Ajout des URLs pour servir les fichiers médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
