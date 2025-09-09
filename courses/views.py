from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.db.models import Count, Avg
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
from django.http import HttpResponse
from .models import Course, Module, Content, TextContent, FileContent, ImageContent, VideoContent
import json
import os

from .models import (
    Category, Course, Module, TextContent, FileContent, 
    ImageContent, VideoContent, Enrollment, Progress
)
from .forms import (
    CourseCreateForm, CourseUpdateForm, ModuleCreateForm, 
    TextContentForm, FileContentForm, ImageContentForm, VideoContentForm
)
from certificates.models import Certificate

def home(request):
    """Page d'accueil avec les cours populaires et récents"""
    categories = Category.objects.all()
    popular_courses = Course.objects.filter(status='published').annotate(
        student_count=Count('students')).order_by('-student_count')[:6]
    recent_courses = Course.objects.filter(status='published').order_by('-created')[:6]
    
    return render(request, 'courses/home.html', {
        'categories': categories,
        'popular_courses': popular_courses,
        'recent_courses': recent_courses
    })

def course_list(request, category_slug=None):
    """Liste des cours disponibles avec filtrage par catégorie"""
    categories = Category.objects.all()
    category = None
    courses = Course.objects.filter(status='published')
    
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        courses = courses.filter(category=category)
    
    return render(request, 'courses/course_list.html', {
        'categories': categories,
        'category': category,
        'courses': courses
    })

def course_detail(request, slug):
    """Détails d'un cours spécifique"""
    course = get_object_or_404(Course, slug=slug, status='published')
    modules = course.modules.all()
    enrolled = False
    if request.user.is_authenticated:
        enrolled = Enrollment.objects.filter(student=request.user, course=course).exists()
    
    return render(request, 'courses/course_detail.html', {
        'course': course,
        'modules': modules,
        'enrolled': enrolled
    })

@login_required
def course_enroll(request, slug):
    """Inscription à un cours"""
    course = get_object_or_404(Course, slug=slug, status='published')
    
    # Vérifier si l'utilisateur est déjà inscrit
    if Enrollment.objects.filter(student=request.user, course=course).exists():
        messages.info(request, f'Vous êtes déjà inscrit au cours {course.title}.')
    else:
        # Créer l'inscription
        Enrollment.objects.create(student=request.user, course=course)
        messages.success(request, f'Vous êtes maintenant inscrit au cours {course.title}.')
    
    return redirect('courses:course_learn', slug=slug)

@login_required
def course_learn(request, slug):
    """Page principale d'apprentissage d'un cours"""
    course = get_object_or_404(Course, slug=slug)
    
    # Vérifier si l'utilisateur est inscrit
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
    
    modules = course.modules.all()
    
    # Trouver le premier module non complété
    current_module = None
    for module in modules:
        progress, created = Progress.objects.get_or_create(
            student=request.user, 
            course=course,
            module=module
        )
        if not progress.completed:
            current_module = module
            break
    
    # Si tous les modules sont complétés ou aucun module n'existe
    if not current_module and modules.exists():
        current_module = modules.first()
    
    # Obtenir les IDs des modules complétés
    completed_module_ids = Progress.objects.filter(
        student=request.user,
        course=course,
        completed=True
    ).values_list('module_id', flat=True)
    
    # Calculer la progression globale
    completed_modules_count = len(completed_module_ids)
    
    total_modules = modules.count()
    progress_percentage = 0
    if total_modules > 0:
        progress_percentage = (completed_modules_count / total_modules) * 100
    
    # Récupérer le certificat s'il existe
    certificate = None
    try:
        certificate = Certificate.objects.get(student=request.user, course=course)
    except Certificate.DoesNotExist:
        certificate = None
    
    return render(request, 'courses/course_learn.html', {
        'course': course,
        'modules': modules,
        'current_module': current_module,
        'progress_percentage': progress_percentage,
        'enrollment': enrollment,
        'completed_modules': completed_module_ids,
        'certificate': certificate
    })

@login_required
def module_content(request, slug, module_id):
    """Affiche le contenu d'un module spécifique"""
    course = get_object_or_404(Course, slug=slug)
    
    # Vérifier si l'utilisateur est inscrit
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
    
    module = get_object_or_404(Module, id=module_id, course=course)
    
    # Récupérer tous les contenus différents
    text_contents = TextContent.objects.filter(module=module).order_by('order')
    file_contents = FileContent.objects.filter(module=module).order_by('order')
    image_contents = ImageContent.objects.filter(module=module).order_by('order')
    video_contents = VideoContent.objects.filter(module=module).order_by('order')
    
    # Mettre à jour la progression
    progress, created = Progress.objects.get_or_create(
        student=request.user,
        course=course,
        module=module
    )
    
    # Obtenir les IDs des modules complétés
    completed_modules = Progress.objects.filter(
        student=request.user,
        course=course,
        completed=True
    ).values_list('module_id', flat=True)
    
    # Récupérer les quiz associés au module
    from quizzes.models import Quiz, QuizAttempt
    quizzes = Quiz.objects.filter(module=module)
    
    # Récupérer les informations sur les tentatives de quiz de l'étudiant
    student_quiz_attempts = {}
    for quiz in quizzes:
        attempts = QuizAttempt.objects.filter(student=request.user, quiz=quiz).order_by('-start_time')
        passed = attempts.filter(passed=True).exists()
        last_attempt_id = attempts.first().id if attempts.exists() else None
        student_quiz_attempts[quiz.id] = {
            'attempts': attempts.exists(),
            'passed': passed,
            'last_attempt_id': last_attempt_id
        }
    
    # Marquer comme complété si l'utilisateur soumet le formulaire
    if request.method == 'POST':
        if 'complete_module' in request.POST:
            progress.completed = True
            progress.save()
            messages.success(request, f'Module {module.title} marqué comme complété!')
            
            # Rediriger vers le prochain module ou retour à la page du cours
            next_module = Module.objects.filter(course=course, order__gt=module.order).first()
            if next_module:
                return redirect('courses:module_content', slug=slug, module_id=next_module.id)
            else:
                return redirect('courses:course_learn', slug=slug)
    
    return render(request, 'courses/module_content.html', {
        'course': course,
        'module': module,
        'text_contents': text_contents,
        'file_contents': file_contents,
        'image_contents': image_contents,
        'video_contents': video_contents,
        'progress': progress,
        'enrollment': enrollment,
        'completed_modules': completed_modules,
        'quizzes': quizzes,
        'student_quiz_attempts': student_quiz_attempts
    })

@login_required
def course_complete(request, slug):
    """Compléter un cours et générer un certificat"""
    course = get_object_or_404(Course, slug=slug)
    enrollment = get_object_or_404(Enrollment, student=request.user, course=course)
    
    # Vérifier si tous les modules sont complétés
    modules = course.modules.all()
    all_completed = True
    
    for module in modules:
        progress = Progress.objects.filter(
            student=request.user,
            course=course,
            module=module,
            completed=True
        ).exists()
        
        if not progress:
            all_completed = False
            break
    
    if all_completed:
        # Marquer le cours comme complété
        enrollment.completed = True
        enrollment.save()
        
        # Générer un certificat si ce n'est pas déjà fait
        certificate, created = Certificate.objects.get_or_create(
            student=request.user,
            course=course
        )
        
        messages.success(request, f'Félicitations! Vous avez complété le cours {course.title}.')
        return redirect('certificates:certificate_detail', certificate_id=certificate.certificate_id)
    else:
        messages.warning(request, 'Vous devez compléter tous les modules avant de terminer ce cours.')
        return redirect('courses:course_learn', slug=slug)

# Vues pour les instructeurs

@login_required
def instructor_courses(request):
    """Liste des cours créés par l'instructeur"""
    if not request.user.is_instructor:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    courses = Course.objects.filter(instructor=request.user)
    return render(request, 'courses/instructor/course_list.html', {
        'courses': courses
    })

@login_required
def course_create(request):
    """Créer un nouveau cours"""
    if not request.user.is_instructor:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    if request.method == 'POST':
        form = CourseCreateForm(request.POST, request.FILES)
        if form.is_valid():
            course = form.save(commit=False)
            course.instructor = request.user
            course.save()
            messages.success(request, f'Le cours "{course.title}" a été créé avec succès.')
            return redirect('courses:course_modules', slug=course.slug)
    else:
        form = CourseCreateForm()
    
    return render(request, 'courses/instructor/course_create.html', {
        'form': form
    })

@login_required
def course_edit(request, slug):
    """Modifier un cours existant"""
    if not request.user.is_instructor:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    
    if request.method == 'POST':
        form = CourseUpdateForm(request.POST, request.FILES, instance=course)
        if form.is_valid():
            course = form.save(commit=False)
            # Mise à jour explicite du statut
            course.status = form.cleaned_data['status']
            course.save()
            messages.success(request, f'Le cours "{course.title}" a été mis à jour avec succès.')
            return redirect('courses:instructor_courses')
    else:
        form = CourseUpdateForm(instance=course)
    
    return render(request, 'courses/instructor/course_edit.html', {
        'form': form,
        'course': course
    })

@login_required
def course_delete(request, slug):
    """Supprimer un cours"""
    if not request.user.is_instructor:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    
    if request.method == 'POST':
        course.delete()
        messages.success(request, f'Le cours "{course.title}" a été supprimé avec succès.')
        return redirect('courses:instructor_courses')
    
    return render(request, 'courses/instructor/course_delete.html', {
        'course': course
    })

@login_required
def course_modules(request, slug):
    """Gérer les modules d'un cours"""
    if not request.user.is_instructor:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    modules = course.modules.all()
    
    if request.method == 'POST':
        form = ModuleCreateForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.course = course
            module.order = modules.count() + 1  # Placer à la fin
            module.save()
            messages.success(request, f'Le module "{module.title}" a été ajouté avec succès.')
            return redirect('courses:course_modules', slug=slug)
    else:
        form = ModuleCreateForm()
    
    return render(request, 'courses/instructor/course_modules.html', {
        'course': course,
        'modules': modules,
        'form': form
    })

@login_required
def module_content_list(request, module_id):
    """Gérer le contenu d'un module"""
    if not request.user.is_instructor:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    module = get_object_or_404(Module, id=module_id, course__instructor=request.user)
    course = module.course
    
    # Récupérer tous les contenus différents
    text_contents = TextContent.objects.filter(module=module).order_by('order')
    file_contents = FileContent.objects.filter(module=module).order_by('order')
    image_contents = ImageContent.objects.filter(module=module).order_by('order')
    video_contents = VideoContent.objects.filter(module=module).order_by('order')
    
    # Récupérer les quizzes du module
    from quizzes.models import Quiz
    quizzes = Quiz.objects.filter(module=module)
    
    return render(request, 'courses/instructor/module_content_list.html', {
        'module': module,
        'course': course,
        'text_contents': text_contents,
        'file_contents': file_contents,
        'image_contents': image_contents,
        'video_contents': video_contents,
        'quizzes': quizzes
    })

@login_required
def content_create(request, module_id, content_type):
    """Créer un nouveau contenu pour un module"""
    if not request.user.is_instructor:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    module = get_object_or_404(Module, id=module_id, course__instructor=request.user)
    
    if content_type == 'text':
        model = TextContent
        form_class = TextContentForm
    elif content_type == 'file':
        model = FileContent
        form_class = FileContentForm
    elif content_type == 'image':
        model = ImageContent
        form_class = ImageContentForm
    elif content_type == 'video':
        model = VideoContent
        form_class = VideoContentForm
    else:
        return redirect('courses:module_content_list', module_id=module_id)
    
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES)
        if form.is_valid():
            content = form.save(commit=False)
            content.module = module
            
            # Déterminer l'ordre
            existing_count = model.objects.filter(module=module).count()
            content.order = existing_count + 1
            
            content.save()
            messages.success(request, f'Le contenu "{content.title}" a été ajouté avec succès.')
            return redirect('courses:module_content_list', module_id=module_id)
    else:
        form = form_class()
    
    template_name = f'courses/instructor/content_create_{content_type}.html'
    return render(request, template_name, {
        'form': form,
        'module': module
    })

@login_required
def content_edit(request, content_id):
    """Modifier un contenu existant"""
    pass  # À implémenter

@login_required
def content_delete(request, content_id):
    # Try to find the content in any of the content type models
    content = None
    content_type = None
    
    # Check each content type model
    for model, type_name in [
        (TextContent, 'text'),
        (FileContent, 'file'), 
        (ImageContent, 'image'),
        (VideoContent, 'video')
    ]:
        try:
            content = model.objects.get(id=content_id)
            content_type = type_name
            break
        except model.DoesNotExist:
            continue
    
    # If content not found in any model, return 404
    if content is None:
        from django.http import Http404
        raise Http404("Content not found")
    
    module = content.module
    course = module.course
    
    # Check if user is the instructor of this course
    if course.instructor != request.user:
        messages.error(request, "Vous n'avez pas la permission de supprimer ce contenu.")
        return redirect('courses:course_list')
    
    if request.method == 'POST':
        content_title = content.title
        
        # Delete physical files if they exist
        if hasattr(content, 'file') and content.file:
            try:
                if os.path.isfile(content.file.path):
                    os.remove(content.file.path)
            except OSError:
                pass
        
        if hasattr(content, 'image') and content.image:
            try:
                if os.path.isfile(content.image.path):
                    os.remove(content.image.path)
            except OSError:
                pass
        
        content.delete()
        messages.success(request, f'Le contenu "{content_title}" a été supprimé avec succès.')
        return redirect('courses:module_content_list', module_id=module.id)
    
    context = {
        'content': content,
        'module': module,
        'course': course,
        'content_type': content_type,
    }
    return render(request, 'courses/instructor/content_confirm_delete.html', context)

@login_required
def course_students(request, slug):
    """Voir les étudiants inscrits à un cours"""
    if not request.user.is_instructor:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    enrollments = course.enrollments.all()
    
    return render(request, 'courses/instructor/course_students.html', {
        'course': course,
        'enrollments': enrollments
    })

@login_required
def student_progress(request, slug, student_id):
    """Voir la progression d'un étudiant spécifique"""
    if not request.user.is_instructor:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    course = get_object_or_404(Course, slug=slug, instructor=request.user)
    enrollment = get_object_or_404(Enrollment, course=course, student_id=student_id)
    student = enrollment.student
    
    # Récupérer les progrès de l'étudiant pour chaque module
    progresses = Progress.objects.filter(student=student, course=course)
    
    return render(request, 'courses/instructor/student_progress.html', {
        'course': course,
        'student': student,
        'enrollment': enrollment,
        'progresses': progresses
    })

# Ajoutez cette fonction complète à la fin de votre views.py
@login_required
@require_POST
def delete_module(request, course_id, module_id):
    """Supprimer un module avec tous ses contenus"""
    print(f"Delete module called: course_id={course_id}, module_id={module_id}")  # Debug
    
    # Vérifier si l'utilisateur est instructeur
    if not hasattr(request.user, 'is_instructor') or not request.user.is_instructor:
        return JsonResponse({'success': False, 'error': 'Permission denied'}, status=403)
    
    try:
        course = get_object_or_404(Course, id=course_id, instructor=request.user)
        module = get_object_or_404(Module, id=module_id, course=course)
    except Exception as e:
        print(f"Error finding course/module: {e}")
        return JsonResponse({'success': False, 'error': 'Cours ou module introuvable'}, status=404)
    
    try:
        with transaction.atomic():
            module_title = module.title
            
            # Compter les éléments
            text_count = module.text_contents.count()
            file_count = module.file_contents.count()
            image_count = module.image_contents.count()
            video_count = module.video_contents.count()
            progress_count = module.student_progress.count()
            
            # Supprimer les fichiers physiques
            for file_content in module.file_contents.all():
                if file_content.file and os.path.isfile(file_content.file.path):
                    try:
                        os.remove(file_content.file.path)
                    except OSError:
                        pass
            
            for image_content in module.image_contents.all():
                if image_content.image and os.path.isfile(image_content.image.path):
                    try:
                        os.remove(image_content.image.path)
                    except OSError:
                        pass
            
            # Supprimer le module
            module.delete()
            
            # Réorganiser l'ordre
            remaining_modules = Module.objects.filter(course=course).order_by('order')
            for index, mod in enumerate(remaining_modules, 1):
                mod.order = index
                mod.save()
            
            total_deleted = text_count + file_count + image_count + video_count
            
            print(f"Module {module_title} deleted successfully")  # Debug
            
            return JsonResponse({
                'success': True, 
                'message': f'Module "{module_title}" supprimé avec succès.',
                'details': {
                    'text_contents': text_count,
                    'file_contents': file_count,
                    'image_contents': image_count,
                    'video_contents': video_count,
                    'progress_records': progress_count,
                    'total_contents': total_deleted
                }
            })
            
    except Exception as e:
        print(f"Error deleting module: {e}")  # Debug
        return JsonResponse({'success': False, 'error': f'Erreur lors de la suppression: {str(e)}'}, status=500)