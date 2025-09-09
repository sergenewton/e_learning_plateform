from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.utils import timezone
from django.forms import inlineformset_factory

from .models import Quiz, Question, Answer, QuizAttempt, QuestionResponse
from courses.models import Module
from .forms import (
    QuizForm, QuestionForm, AnswerFormSet, 
    MultipleChoiceResponseForm, SingleChoiceResponseForm,
    TrueFalseResponseForm, ShortAnswerResponseForm
)

# Vues pour les étudiants

@login_required
def take_quiz(request, quiz_id):
    """Vue pour passer un quiz"""
    quiz = get_object_or_404(Quiz, id=quiz_id)
    module = quiz.module
    course = module.course
    
    # Vérifier si l'étudiant est inscrit au cours
    if not course.students.filter(id=request.user.id).exists():
        messages.error(request, "Vous devez être inscrit au cours pour passer ce quiz.")
        return redirect('courses:course_detail', slug=course.slug)
    
    # Vérifier si l'étudiant a déjà une tentative réussie
    passed_attempt = QuizAttempt.objects.filter(
        student=request.user, quiz=quiz, passed=True
    ).exists()
    
    if passed_attempt:
        messages.info(request, "Vous avez déjà réussi ce quiz.")
        return redirect('courses:module_content', slug=course.slug, module_id=module.id)
    
    # Créer une nouvelle tentative
    if request.method == 'POST':
        # Créer une tentative
        attempt = QuizAttempt.objects.create(
            student=request.user,
            quiz=quiz,
            start_time=timezone.now()
        )
        
        # Traiter les réponses
        questions = quiz.questions.all().order_by('order')
        total_points = sum(question.points for question in questions)
        earned_points = 0
        
        for question in questions:
            is_correct = False
            
            if question.question_type == 'multiple_choice':
                # Gérer les questions à choix multiples
                selected_answer_ids = request.POST.getlist(f'question_{question.id}')
                selected_answers = Answer.objects.filter(id__in=selected_answer_ids, question=question)
                
                # Vérifier si toutes les bonnes réponses sont sélectionnées et aucune mauvaise réponse
                correct_answers = question.answers.filter(is_correct=True)
                if (set(selected_answers) == set(correct_answers)) and len(selected_answers) > 0:
                    is_correct = True
                    earned_points += question.points
                
                # Créer la réponse à la question
                question_response = QuestionResponse.objects.create(
                    attempt=attempt,
                    question=question,
                    is_correct=is_correct
                )
                question_response.selected_answers.set(selected_answers)
                
            elif question.question_type == 'single_choice':
                # Gérer les questions à choix unique
                selected_answer_id = request.POST.get(f'question_{question.id}')
                if selected_answer_id:
                    selected_answer = get_object_or_404(Answer, id=selected_answer_id, question=question)
                    
                    # Vérifier si la réponse est correcte
                    if selected_answer.is_correct:
                        is_correct = True
                        earned_points += question.points
                    
                    # Créer la réponse à la question
                    question_response = QuestionResponse.objects.create(
                        attempt=attempt,
                        question=question,
                        is_correct=is_correct
                    )
                    question_response.selected_answers.add(selected_answer)
                    
            elif question.question_type == 'true_false':
                # Gérer les questions vrai/faux
                selected_answer_id = request.POST.get(f'question_{question.id}')
                if selected_answer_id:
                    selected_answer = get_object_or_404(Answer, id=selected_answer_id, question=question)
                    
                    # Vérifier si la réponse est correcte
                    if selected_answer.is_correct:
                        is_correct = True
                        earned_points += question.points
                    
                    # Créer la réponse à la question
                    question_response = QuestionResponse.objects.create(
                        attempt=attempt,
                        question=question,
                        is_correct=is_correct
                    )
                    question_response.selected_answers.add(selected_answer)
                    
            elif question.question_type == 'short_answer':
                # Gérer les questions à réponse courte
                text_response = request.POST.get(f'question_{question.id}', '').strip()
                
                # Ici, on pourrait comparer avec des réponses attendues ou faire une analyse plus avancée
                correct_answers = Answer.objects.filter(question=question, is_correct=True)
                # Comparer la réponse avec les réponses correctes (ignorer la casse)
                for answer in correct_answers:
                    if text_response.lower() == answer.text.lower():
                        is_correct = True
                        earned_points += question.points
                        break
                
                # Créer la réponse à la question
                QuestionResponse.objects.create(
                    attempt=attempt,
                    question=question,
                    text_response=text_response,
                    is_correct=is_correct
                )
        
        # Calculer le score final et déterminer si l'étudiant a réussi
        if total_points > 0:
            score = (earned_points / total_points) * 100
        else:
            score = 0
        
        passed = score >= quiz.required_score_to_pass
        
        attempt.score = score
        attempt.passed = passed
        attempt.end_time = timezone.now()
        attempt.save()
        
        return redirect('quiz_result', attempt_id=attempt.id)
        
    else:
        questions = quiz.questions.all().order_by('order')
        
        return render(request, 'quizzes/take_quiz.html', {
            'quiz': quiz,
            'questions': questions,
            'course': course,
            'module': module,
        })

@login_required
def quiz_result(request, attempt_id):
    """Affichage des résultats d'une tentative de quiz"""
    attempt = get_object_or_404(QuizAttempt, id=attempt_id, student=request.user)
    quiz = attempt.quiz
    module = quiz.module
    course = module.course
    
    # Récupérer les réponses données
    responses = attempt.responses.all()
    
    return render(request, 'quizzes/quiz_result.html', {
        'attempt': attempt,
        'quiz': quiz,
        'course': course,
        'module': module,
        'responses': responses
    })

@login_required
def student_quiz_attempts(request):
    """Affichage de l'historique des tentatives de quiz d'un étudiant"""
    attempts = QuizAttempt.objects.filter(student=request.user).order_by('-start_time')
    
    return render(request, 'quizzes/student_quiz_attempts.html', {
        'attempts': attempts
    })

# Vues pour les instructeurs

@login_required
def create_quiz(request, module_id):
    """Création d'un quiz pour un module"""
    if not request.user.is_instructor:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    module = get_object_or_404(Module, id=module_id, course__instructor=request.user)
    course = module.course
    
    if request.method == 'POST':
        form = QuizForm(request.POST)
        if form.is_valid():
            quiz = form.save(commit=False)
            quiz.module = module
            quiz.save()
            messages.success(request, f"Le quiz '{quiz.title}' a été créé avec succès.")
            return redirect('quiz_questions', quiz_id=quiz.id)
    else:
        form = QuizForm()
    
    return render(request, 'quizzes/instructor/create_quiz.html', {
        'form': form,
        'module': module,
        'course': course
    })

@login_required
def edit_quiz(request, quiz_id):
    """Modification d'un quiz existant"""
    if not request.user.is_instructor:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    quiz = get_object_or_404(Quiz, id=quiz_id, module__course__instructor=request.user)
    module = quiz.module
    course = module.course
    
    if request.method == 'POST':
        form = QuizForm(request.POST, instance=quiz)
        if form.is_valid():
            form.save()
            messages.success(request, f"Le quiz '{quiz.title}' a été mis à jour avec succès.")
            return redirect('quiz_questions', quiz_id=quiz.id)
    else:
        form = QuizForm(instance=quiz)
    
    return render(request, 'quizzes/instructor/edit_quiz.html', {
        'form': form,
        'quiz': quiz,
        'module': module,
        'course': course
    })

@login_required
def delete_quiz(request, quiz_id):
    """Suppression d'un quiz"""
    if not request.user.is_instructor:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    quiz = get_object_or_404(Quiz, id=quiz_id, module__course__instructor=request.user)
    module = quiz.module
    course = module.course
    
    if request.method == 'POST':
        quiz.delete()
        messages.success(request, f"Le quiz '{quiz.title}' a été supprimé avec succès.")
        return redirect('courses:module_content_list', module_id=module.id)
    
    return render(request, 'quizzes/instructor/delete_quiz.html', {
        'quiz': quiz,
        'module': module,
        'course': course
    })

@login_required
def quiz_questions(request, quiz_id):
    """Gestion des questions d'un quiz"""
    if not request.user.is_instructor:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    quiz = get_object_or_404(Quiz, id=quiz_id, module__course__instructor=request.user)
    module = quiz.module
    course = module.course
    questions = quiz.questions.all().order_by('order')
    
    return render(request, 'quizzes/instructor/quiz_questions.html', {
        'quiz': quiz,
        'module': module,
        'course': course,
        'questions': questions
    })

@login_required
def create_question(request, quiz_id):
    """Création d'une question pour un quiz"""
    if not request.user.is_instructor:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    quiz = get_object_or_404(Quiz, id=quiz_id, module__course__instructor=request.user)
    module = quiz.module
    course = module.course
    
    # Déterminer l'ordre de la nouvelle question
    next_order = quiz.questions.count() + 1
    
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.quiz = quiz
            question.order = next_order
            question.save()
            
            # Rediriger pour ajouter les réponses à la question
            messages.success(request, "Question créée avec succès. Ajoutez maintenant les réponses.")
            return redirect('edit_question', question_id=question.id)
    else:
        form = QuestionForm()
    
    return render(request, 'quizzes/instructor/create_question.html', {
        'form': form,
        'quiz': quiz,
        'module': module,
        'course': course
    })

@login_required
def edit_question(request, question_id):
    """Modification d'une question et de ses réponses"""
    if not request.user.is_instructor:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    question = get_object_or_404(Question, id=question_id, quiz__module__course__instructor=request.user)
    quiz = question.quiz
    module = quiz.module
    course = module.course
    
    AnswerInlineFormSet = inlineformset_factory(
        Question,
        Answer,
        fields=['text', 'is_correct'],
        extra=4,
        can_delete=True
    )
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        formset = AnswerInlineFormSet(request.POST, instance=question)
        
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, "Question et réponses mises à jour avec succès.")
            return redirect('quiz_questions', quiz_id=quiz.id)
    else:
        form = QuestionForm(instance=question)
        formset = AnswerInlineFormSet(instance=question)
    
    return render(request, 'quizzes/instructor/edit_question.html', {
        'form': form,
        'formset': formset,
        'question': question,
        'quiz': quiz,
        'module': module,
        'course': course
    })

@login_required
def delete_question(request, question_id):
    """Suppression d'une question"""
    if not request.user.is_instructor:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    question = get_object_or_404(Question, id=question_id, quiz__module__course__instructor=request.user)
    quiz = question.quiz
    module = quiz.module
    course = module.course
    
    if request.method == 'POST':
        question.delete()
        messages.success(request, "Question supprimée avec succès.")
        return redirect('quiz_questions', quiz_id=quiz.id)
    
    return render(request, 'quizzes/instructor/delete_question.html', {
        'question': question,
        'quiz': quiz,
        'module': module,
        'course': course
    })

@login_required
def quiz_results(request, quiz_id):
    """Affichage de tous les résultats d'un quiz"""
    if not request.user.is_instructor:
        return HttpResponseForbidden("Vous n'avez pas l'autorisation d'accéder à cette page.")
    
    quiz = get_object_or_404(Quiz, id=quiz_id, module__course__instructor=request.user)
    module = quiz.module
    course = module.course
    
    attempts = QuizAttempt.objects.filter(quiz=quiz).order_by('-start_time')
    
    # Calcul des statistiques
    total_attempts = attempts.count()
    passed_attempts = attempts.filter(passed=True).count()
    
    pass_rate = 0
    avg_score = 0
    
    if total_attempts > 0:
        pass_rate = (passed_attempts / total_attempts) * 100
        avg_score = sum(a.score or 0 for a in attempts) / total_attempts
    
    return render(request, 'quizzes/instructor/quiz_results.html', {
        'quiz': quiz,
        'module': module,
        'course': course,
        'attempts': attempts,
        'total_attempts': total_attempts,
        'passed_attempts': passed_attempts,
        'pass_rate': pass_rate,
        'avg_score': avg_score
    })
