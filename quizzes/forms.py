from django import forms
from .models import Quiz, Question, Answer

class QuizForm(forms.ModelForm):
    """Formulaire pour créer et modifier un quiz"""
    
    class Meta:
        model = Quiz
        fields = ['title', 'description', 'time_limit', 'required_score_to_pass']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'required_score_to_pass': 'Score minimum en pourcentage pour réussir ce quiz',
            'time_limit': 'Temps maximum en minutes pour compléter ce quiz'
        }

class QuestionForm(forms.ModelForm):
    """Formulaire pour créer et modifier une question"""
    
    class Meta:
        model = Question
        fields = ['text', 'question_type', 'points']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
        }
        help_texts = {
            'points': 'Nombre de points attribués pour cette question',
            'question_type': 'Le type de question détermine comment les réponses seront présentées'
        }

# Utilise un formset pour gérer plusieurs réponses à la fois
AnswerFormSet = forms.inlineformset_factory(
    Question,
    Answer,
    fields=['text', 'is_correct'],
    extra=4,
    can_delete=True,
    widgets={'text': forms.TextInput(attrs={'class': 'form-control'})},
    labels={'is_correct': 'Réponse correcte'}
)

# Formulaires pour les différents types de réponses (côté étudiant)
class MultipleChoiceResponseForm(forms.Form):
    """Formulaire pour répondre aux questions à choix multiples"""
    def __init__(self, *args, question=None, **kwargs):
        super().__init__(*args, **kwargs)
        if question:
            choices = [(answer.id, answer.text) for answer in question.answers.all()]
            self.fields['answers'] = forms.MultipleChoiceField(
                choices=choices,
                widget=forms.CheckboxSelectMultiple,
                required=False
            )

class SingleChoiceResponseForm(forms.Form):
    """Formulaire pour répondre aux questions à choix unique"""
    def __init__(self, *args, question=None, **kwargs):
        super().__init__(*args, **kwargs)
        if question:
            choices = [(answer.id, answer.text) for answer in question.answers.all()]
            self.fields['answer'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                required=False
            )

class TrueFalseResponseForm(forms.Form):
    """Formulaire pour répondre aux questions vrai/faux"""
    def __init__(self, *args, question=None, **kwargs):
        super().__init__(*args, **kwargs)
        if question:
            choices = [(answer.id, answer.text) for answer in question.answers.all()]
            self.fields['answer'] = forms.ChoiceField(
                choices=choices,
                widget=forms.RadioSelect,
                required=False
            )

class ShortAnswerResponseForm(forms.Form):
    """Formulaire pour répondre aux questions à réponse courte"""
    answer = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )