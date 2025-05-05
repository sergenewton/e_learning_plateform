from django.db import models
from django.conf import settings
from courses.models import Module

User = settings.AUTH_USER_MODEL

class Quiz(models.Model):
    """Quiz associé à un module de cours"""
    module = models.ForeignKey(Module, related_name='quizzes', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    time_limit = models.PositiveIntegerField(help_text="Durée en minutes", default=30)
    required_score_to_pass = models.PositiveIntegerField(help_text="Score minimum pour réussir en %", default=70)
    
    class Meta:
        verbose_name_plural = "Quizzes"
    
    def __str__(self):
        return f"Quiz: {self.title}"

class Question(models.Model):
    """Question de quiz avec plusieurs types possibles"""
    QUESTION_TYPES = (
        ('multiple_choice', 'Choix multiple'),
        ('single_choice', 'Choix unique'),
        ('true_false', 'Vrai ou Faux'),
        ('short_answer', 'Réponse courte'),
    )
    
    quiz = models.ForeignKey(Quiz, related_name='questions', on_delete=models.CASCADE)
    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES)
    points = models.PositiveIntegerField(default=1)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"Question {self.order}: {self.text[:50]}..."

class Answer(models.Model):
    """Réponses possibles pour les questions"""
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Réponse: {self.text[:50]}"

class QuizAttempt(models.Model):
    """Tentative d'un étudiant pour compléter un quiz"""
    student = models.ForeignKey(User, related_name='quiz_attempts', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, related_name='attempts', on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    score = models.FloatField(null=True, blank=True)
    passed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Tentative de {self.student.username} pour {self.quiz.title}"

class QuestionResponse(models.Model):
    """Réponse d'un étudiant à une question spécifique"""
    attempt = models.ForeignKey(QuizAttempt, related_name='responses', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='student_responses', on_delete=models.CASCADE)
    selected_answers = models.ManyToManyField(Answer, related_name='selected_by', blank=True)
    text_response = models.TextField(blank=True)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"Réponse à {self.question}"
