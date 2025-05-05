from django.urls import path
from . import views

urlpatterns = [
    # URLs pour les étudiants
    path('attempt/<int:quiz_id>/', views.take_quiz, name='take_quiz'),
    path('attempt/<int:attempt_id>/result/', views.quiz_result, name='quiz_result'),
    path('my-attempts/', views.student_quiz_attempts, name='student_quiz_attempts'),
    
    # URLs pour les instructeurs
    path('module/<int:module_id>/create/', views.create_quiz, name='create_quiz'),
    path('<int:quiz_id>/edit/', views.edit_quiz, name='edit_quiz'),
    path('<int:quiz_id>/delete/', views.delete_quiz, name='delete_quiz'),
    path('<int:quiz_id>/questions/', views.quiz_questions, name='quiz_questions'),
    path('<int:quiz_id>/question/create/', views.create_question, name='create_question'),
    path('question/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('results/<int:quiz_id>/', views.quiz_results, name='quiz_results'),
]