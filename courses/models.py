from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify

User = settings.AUTH_USER_MODEL

class Category(models.Model):
    """Catégories de cours (ex: Programmation, Design, Business...)"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "Categories"

class Course(models.Model):
    """Modèle principal pour les cours"""
    STATUS_CHOICES = (
        ('draft', 'Brouillon'),
        ('published', 'Publié'),
    )
    LEVEL_CHOICES = (
        ('beginner', 'Débutant'),
        ('intermediate', 'Intermédiaire'),
        ('advanced', 'Avancé'),
    )
    
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    category = models.ForeignKey(Category, related_name='courses', on_delete=models.CASCADE)
    instructor = models.ForeignKey(User, related_name='courses_created', on_delete=models.CASCADE)
    students = models.ManyToManyField(User, related_name='courses_enrolled', blank=True)
    level = models.CharField(max_length=15, choices=LEVEL_CHOICES, default='beginner')
    thumbnail = models.ImageField(upload_to='course_thumbnails/', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('course_detail', args=[self.slug])
    
    class Meta:
        ordering = ['-created']

class Module(models.Model):
    """Modules qui composent un cours"""
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.order}. {self.title}"
    
    class Meta:
        ordering = ['order']

class Content(models.Model):
    """Contenu abstrait qui peut être de différents types (vidéo, texte, fichier, etc.)"""
    title = models.CharField(max_length=200)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        abstract = True
        ordering = ['order']
    
    def __str__(self):
        return self.title

class TextContent(Content):
    """Contenu de type texte"""
    module = models.ForeignKey(Module, related_name='text_contents', on_delete=models.CASCADE)
    content = models.TextField()

class FileContent(Content):
    """Contenu de type fichier (PDF, etc.)"""
    module = models.ForeignKey(Module, related_name='file_contents', on_delete=models.CASCADE)
    file = models.FileField(upload_to='course_files/')

class ImageContent(Content):
    """Contenu de type image"""
    module = models.ForeignKey(Module, related_name='image_contents', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='course_images/')
    caption = models.CharField(max_length=255, blank=True)

class VideoContent(Content):
    """Contenu de type vidéo"""
    module = models.ForeignKey(Module, related_name='video_contents', on_delete=models.CASCADE)
    url = models.URLField()  # URL de vidéo externe (YouTube, Vimeo, etc.)
    duration = models.PositiveIntegerField(help_text="Durée en minutes", default=0)

class Enrollment(models.Model):
    """Inscription d'un étudiant à un cours"""
    student = models.ForeignKey(User, related_name='enrollments', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='enrollments', on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['student', 'course']
    
    def __str__(self):
        return f"{self.student.username} enrolled in {self.course.title}"

class Progress(models.Model):
    """Suivi de la progression d'un étudiant dans un cours"""
    student = models.ForeignKey(User, related_name='progress', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name='student_progress', on_delete=models.CASCADE)
    module = models.ForeignKey(Module, related_name='student_progress', on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['student', 'module']
    
    def __str__(self):
        return f"{self.student.username}'s progress in {self.module.title}"
