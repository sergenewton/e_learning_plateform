from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Count

from .models import User
from .forms import StudentSignUpForm, InstructorSignUpForm, StudentProfileForm, InstructorProfileForm
from courses.models import Course, Enrollment

def register(request):
    """Vue qui montre les options d'inscription (étudiant ou instructeur)"""
    return render(request, 'accounts/register.html')

class StudentSignUpView(CreateView):
    """Vue pour l'inscription des étudiants"""
    model = User
    form_class = StudentSignUpForm
    template_name = 'accounts/signup_form.html'
    success_url = reverse_lazy('home')
    
    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'étudiant'
        return super().get_context_data(**kwargs)
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Inscription réussie ! Vous êtes maintenant connecté en tant qu'étudiant.")
        return redirect('student_profile')

class InstructorSignUpView(CreateView):
    """Vue pour l'inscription des instructeurs"""
    model = User
    form_class = InstructorSignUpForm
    template_name = 'accounts/signup_form.html'
    success_url = reverse_lazy('home')
    
    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'instructeur'
        return super().get_context_data(**kwargs)
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(self.request, "Inscription réussie ! Vous êtes maintenant connecté en tant qu'instructeur.")
        return redirect('instructor_profile')

@login_required
def student_profile(request):
    """Vue pour le profil d'étudiant"""
    if not request.user.is_student:
        messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette page.")
        return redirect('home')
    
    # Récupérer les cours auxquels l'étudiant est inscrit
    enrollments = Enrollment.objects.filter(student=request.user).order_by('-created')
    
    # Récupérer les certificats de l'étudiant
    certificates = request.user.certificates.all()
    
    # Mettre à jour le profil de l'utilisateur
    if request.method == 'POST':
        form = StudentProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès.")
            return redirect('student_profile')
    else:
        form = StudentProfileForm(instance=request.user)
    
    return render(request, 'accounts/student_profile.html', {
        'form': form,
        'enrollments': enrollments,
        'certificates': certificates
    })

@login_required
def instructor_profile(request):
    """Vue pour le profil d'instructeur"""
    if not request.user.is_instructor:
        messages.error(request, "Vous n'avez pas l'autorisation d'accéder à cette page.")
        return redirect('home')
    
    # Récupérer les cours créés par l'instructeur
    courses = Course.objects.filter(instructor=request.user)
    
    # Compter le nombre d'étudiants et calculer le taux d'achèvement
    course_stats = []
    for course in courses:
        enrollments = course.enrollments.count()
        completed = course.enrollments.filter(completed=True).count()
        completion_rate = (completed / enrollments * 100) if enrollments > 0 else 0
        
        course_stats.append({
            'course': course,
            'students': enrollments,
            'completed': completed,
            'completion_rate': completion_rate
        })
    
    # Mettre à jour le profil de l'instructeur
    if request.method == 'POST':
        form = InstructorProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès.")
            return redirect('instructor_profile')
    else:
        form = InstructorProfileForm(instance=request.user)
    
    return render(request, 'accounts/instructor_profile.html', {
        'form': form,
        'courses': course_stats
    })

def profile_detail(request, username):
    """Vue publique du profil d'un utilisateur"""
    user = get_object_or_404(User, username=username)
    
    context = {'profile_user': user}
    
    if user.is_instructor:
        # Pour les instructeurs, afficher leurs cours
        courses = Course.objects.filter(instructor=user, status='published')
        student_count = User.objects.filter(
            is_student=True, 
            enrollments__course__instructor=user
        ).distinct().count()
        
        context.update({
            'courses': courses,
            'student_count': student_count,
        })
    
    return render(request, 'accounts/profile_detail.html', context)
