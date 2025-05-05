from django.urls import path
from . import views

urlpatterns = [
    # URLs pour les étudiants
    path('my-certificates/', views.student_certificates, name='student_certificates'),
    path('view/<uuid:certificate_id>/', views.certificate_detail, name='certificate_detail'),
    path('download/<uuid:certificate_id>/', views.certificate_download, name='certificate_download'),
    
    # URL publique pour la vérification de certificat
    path('verify/<uuid:certificate_id>/', views.certificate_verify, name='certificate_verify'),
    
    # URLs pour les administrateurs
    path('templates/', views.certificate_templates, name='certificate_templates'),
    path('template/create/', views.create_certificate_template, name='create_certificate_template'),
    path('template/<int:template_id>/edit/', views.edit_certificate_template, name='edit_certificate_template'),
    path('template/<int:template_id>/delete/', views.delete_certificate_template, name='delete_certificate_template'),
]