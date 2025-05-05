from django.db import models
from django.conf import settings
from courses.models import Course
import uuid
from django.utils import timezone

User = settings.AUTH_USER_MODEL

class Certificate(models.Model):
    """Certificat attribué à un étudiant ayant complété un cours"""
    student = models.ForeignKey(User, related_name='certificates', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='certificates', on_delete=models.CASCADE)
    certificate_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    issued_date = models.DateTimeField(default=timezone.now)
    pdf_file = models.FileField(upload_to='certificates/', blank=True, null=True)
    is_valid = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"Certificat de {self.student.username} pour {self.course.title}"
    
    def get_verification_url(self):
        """URL pour vérifier l'authenticité d'un certificat"""
        return f"/certificates/verify/{self.certificate_id}/"

class CertificateTemplate(models.Model):
    """Modèles de certificats personnalisables"""
    name = models.CharField(max_length=100)
    template_file = models.FileField(upload_to='certificate_templates/')
    background_image = models.ImageField(upload_to='certificate_backgrounds/', blank=True, null=True)
    signature_image = models.ImageField(upload_to='certificate_signatures/', blank=True, null=True)
    title_text = models.CharField(max_length=200, default="Certificat d'Accomplissement")
    body_text = models.TextField(default="Ce certificat est décerné à {student_name} pour avoir complété avec succès le cours {course_title}.")
    is_default = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
