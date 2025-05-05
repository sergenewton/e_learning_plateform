from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction

from .models import User, StudentProfile, InstructorProfile

class StudentSignUpForm(UserCreationForm):
    """Formulaire d'inscription pour les étudiants"""
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    email = forms.EmailField(required=True, label="E-mail")
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'password1', 'password2')
    
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_student = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.save()
        return user

class InstructorSignUpForm(UserCreationForm):
    """Formulaire d'inscription pour les instructeurs"""
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    email = forms.EmailField(required=True, label="E-mail")
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False, label="Biographie")
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'bio', 'password1', 'password2')
    
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_instructor = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.bio = self.cleaned_data.get('bio')
        user.save()
        return user

class StudentProfileForm(forms.ModelForm):
    """Formulaire de modification du profil étudiant"""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'profile_picture', 'bio')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class InstructorProfileForm(forms.ModelForm):
    """Formulaire de modification du profil instructeur"""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'profile_picture', 'bio')
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class InstructorExtraProfileForm(forms.ModelForm):
    """Formulaire de modification des informations spécifiques à l'instructeur"""
    
    class Meta:
        model = InstructorProfile
        fields = ('expertise', 'experience_years', 'qualification')
        widgets = {
            'qualification': forms.Textarea(attrs={'rows': 3}),
        }