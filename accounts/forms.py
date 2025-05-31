from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.db import transaction

from .models import User, StudentProfile, InstructorProfile

class StudentSignUpForm(UserCreationForm):
    """Formulaire d'inscription pour les étudiants"""
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    email = forms.EmailField(required=True, label="E-mail")
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False, label="Biographie")
    profile_picture = forms.ImageField(required=False, label="Photo de profil")
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'bio', 'profile_picture', 'password1', 'password2')
    
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_student = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.bio = self.cleaned_data.get('bio')
        if self.cleaned_data.get('profile_picture'):
            user.profile_picture = self.cleaned_data.get('profile_picture')
        user.save()
        return user

class InstructorSignUpForm(UserCreationForm):
    """Formulaire d'inscription pour les instructeurs"""
    first_name = forms.CharField(max_length=30, required=True, label="Prénom")
    last_name = forms.CharField(max_length=30, required=True, label="Nom")
    email = forms.EmailField(required=True, label="E-mail")
    bio = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False, label="Biographie")
    profile_picture = forms.ImageField(required=False, label="Photo de profil")
    website = forms.URLField(required=False, label="Site web")
    qualifications = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False, label="Qualifications")
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'bio', 'profile_picture', 'password1', 'password2')
    
    @transaction.atomic
    def save(self):
        user = super().save(commit=False)
        user.is_instructor = True
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.email = self.cleaned_data.get('email')
        user.bio = self.cleaned_data.get('bio')
        if self.cleaned_data.get('profile_picture'):
            user.profile_picture = self.cleaned_data.get('profile_picture')
        user.save()
        
        # Create or update instructor profile
        instructor_profile, created = InstructorProfile.objects.get_or_create(user=user)
        instructor_profile.qualification = self.cleaned_data.get('qualifications', '')
        instructor_profile.save()
        
        return user

class StudentProfileForm(forms.ModelForm):
    """Formulaire de modification du profil étudiant"""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'profile_picture', 'bio')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

class InstructorProfileForm(forms.ModelForm):
    """Formulaire de modification du profil instructeur"""
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'profile_picture', 'bio')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

class InstructorExtraProfileForm(forms.ModelForm):
    """Formulaire de modification des informations spécifiques à l'instructeur"""
    
    class Meta:
        model = InstructorProfile
        fields = ('expertise', 'experience_years', 'qualification')
        widgets = {
            'qualification': forms.Textarea(attrs={'rows': 3}),
        }

class CustomPasswordChangeForm(PasswordChangeForm):
    """Formulaire de changement de mot de passe avec des classes Bootstrap"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})