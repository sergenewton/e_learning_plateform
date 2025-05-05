from django import forms
from .models import (
    Course, Module, TextContent, FileContent, 
    ImageContent, VideoContent, Category
)

class CourseCreateForm(forms.ModelForm):
    """Formulaire de création de cours"""
    
    class Meta:
        model = Course
        fields = ['title', 'category', 'overview', 'level', 'thumbnail', 'price']
        widgets = {
            'overview': forms.Textarea(attrs={'rows': 4}),
        }

class CourseUpdateForm(forms.ModelForm):
    """Formulaire de mise à jour de cours"""
    
    class Meta:
        model = Course
        fields = ['title', 'category', 'overview', 'level', 'thumbnail', 'price', 'discount_price', 'status']
        widgets = {
            'overview': forms.Textarea(attrs={'rows': 4}),
        }

class ModuleCreateForm(forms.ModelForm):
    """Formulaire de création de module"""
    
    class Meta:
        model = Module
        fields = ['title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class ModuleUpdateForm(forms.ModelForm):
    """Formulaire de mise à jour de module"""
    
    class Meta:
        model = Module
        fields = ['title', 'description', 'order']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class TextContentForm(forms.ModelForm):
    """Formulaire pour contenu textuel"""
    
    class Meta:
        model = TextContent
        fields = ['title', 'content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10, 'class': 'rich-text-editor'}),
        }

class FileContentForm(forms.ModelForm):
    """Formulaire pour contenu de type fichier"""
    
    class Meta:
        model = FileContent
        fields = ['title', 'file']
        help_texts = {
            'file': 'Formats supportés: PDF, DOC, DOCX, XLS, XLSX, PPT, PPTX, ZIP (max 50MB)'
        }

class ImageContentForm(forms.ModelForm):
    """Formulaire pour contenu de type image"""
    
    class Meta:
        model = ImageContent
        fields = ['title', 'image', 'caption']
        help_texts = {
            'image': 'Formats supportés: JPG, PNG, GIF (max 5MB)'
        }

class VideoContentForm(forms.ModelForm):
    """Formulaire pour contenu de type vidéo"""
    
    class Meta:
        model = VideoContent
        fields = ['title', 'url', 'duration']
        help_texts = {
            'url': 'Entrez une URL YouTube ou Vimeo',
            'duration': 'Durée en minutes'
        }

class CategoryForm(forms.ModelForm):
    """Formulaire pour les catégories de cours"""
    
    class Meta:
        model = Category
        fields = ['name', 'description']