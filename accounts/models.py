from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class User(AbstractUser):
    """Modèle utilisateur personnalisé pour la plateforme e-learning"""
    is_student = models.BooleanField(default=False)
    is_instructor = models.BooleanField(default=False)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    def __str__(self):
        return self.username

class StudentProfile(models.Model):
    """Profil étudiant avec informations supplémentaires"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    education_level = models.CharField(max_length=100, blank=True)
    interests = models.TextField(blank=True)
    
    def __str__(self):
        return f"Profil de {self.user.username}"

class InstructorProfile(models.Model):
    """Profil instructeur avec informations supplémentaires"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='instructor_profile')
    expertise = models.CharField(max_length=100, blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    qualification = models.TextField(blank=True)
    
    def __str__(self):
        return f"Profil instructeur de {self.user.username}"
