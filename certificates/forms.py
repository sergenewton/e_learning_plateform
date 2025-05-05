from django import forms
from .models import CertificateTemplate

class CertificateTemplateForm(forms.ModelForm):
    """Formulaire pour la création et modification des modèles de certificats"""
    
    class Meta:
        model = CertificateTemplate
        fields = ['name', 'template_file', 'background_image', 'signature_image', 
                  'title_text', 'body_text', 'is_default']
        widgets = {
            'body_text': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'title_text': "Ce texte apparaîtra comme titre du certificat",
            'body_text': "Vous pouvez utiliser {student_name} et {course_title} comme variables",
            'is_default': "Si coché, ce modèle sera utilisé par défaut pour tous les certificats"
        }