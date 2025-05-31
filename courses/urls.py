from django.urls import path
from . import views

urlpatterns = [
    # Page d'accueil et liste des cours
    path('', views.home, name='home'),
    path('courses/', views.course_list, name='course_list'),
    path('category/<slug:category_slug>/', views.course_list, name='course_list_by_category'),
    
    # Détails du cours et inscription
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('course/<slug:slug>/enroll/', views.course_enroll, name='course_enroll'),
    
    # Apprentissage et contenu du cours
    path('course/<slug:slug>/learn/', views.course_learn, name='course_learn'),
    path('course/<slug:slug>/module/<int:module_id>/', views.module_content, name='module_content'),
    path('course/<slug:slug>/complete/', views.course_complete, name='course_complete'),
    
    # Gestion des cours (instructeurs)
    path('instructor/courses/', views.instructor_courses, name='instructor_courses'),
    path('instructor/course/create/', views.course_create, name='course_create'),
    path('instructor/course/<slug:slug>/edit/', views.course_edit, name='course_edit'),
    path('instructor/course/<slug:slug>/delete/', views.course_delete, name='course_delete'),
    
    # Gestion des modules et contenus (instructeurs)
    path('instructor/course/<slug:slug>/modules/', views.course_modules, name='course_modules'),
    path('instructor/module/<int:module_id>/content/', views.module_content_list, name='module_content_list'),
    path('instructor/module/<int:module_id>/content/create/<str:content_type>/', views.content_create, name='content_create'),
    path('instructor/content/<int:content_id>/edit/', views.content_edit, name='content_edit'),
    path('instructor/content/<int:content_id>/delete/', views.content_delete, name='content_delete'),
    
    # Suivi des étudiants (instructeurs)
    path('instructor/course/<slug:slug>/students/', views.course_students, name='course_students'),
    path('instructor/course/<slug:slug>/student/<int:student_id>/', views.student_progress, name='student_progress'),
]