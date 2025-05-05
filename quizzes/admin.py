from django.contrib import admin
from .models import Quiz, Question, Answer, QuizAttempt, QuestionResponse

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 4

class QuestionInline(admin.StackedInline):
    model = Question
    extra = 0

@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'module', 'time_limit', 'required_score_to_pass', 'created']
    list_filter = ['module__course', 'created']
    search_fields = ['title', 'description']
    inlines = [QuestionInline]

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['quiz', 'text', 'question_type', 'points', 'order']
    list_filter = ['quiz', 'question_type']
    search_fields = ['text']
    inlines = [AnswerInline]

@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['text', 'question', 'is_correct']
    list_filter = ['question__quiz', 'is_correct']
    search_fields = ['text']

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'quiz', 'start_time', 'end_time', 'score', 'passed']
    list_filter = ['quiz', 'passed', 'start_time']
    search_fields = ['student__username', 'quiz__title']

@admin.register(QuestionResponse)
class QuestionResponseAdmin(admin.ModelAdmin):
    list_display = ['attempt', 'question', 'is_correct']
    list_filter = ['attempt__quiz', 'is_correct']
    search_fields = ['text_response']
