from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import modelformset_factory
from .models import Poll, Choice, Comment, Profile

# Форма для создания опроса
class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ['question']

# Форма для вариантов ответа
class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text']

# Formset для создания нескольких Choice одновременно (например, 3 пустых формы)
ChoiceFormSet = modelformset_factory(
    Choice,
    form=ChoiceForm,
    extra=3,
    max_num=100,
    validate_max=True,
)

# Форма для комментариев
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']

# Форма регистрации пользователя, добавляем поле email
class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

# Форма для обновления профиля с редактируемым email пользователя
class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = Profile
        fields = ['avatar', 'about']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            self.fields['email'].initial = self.user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
                profile.save()
        return profile

from .models import Poll, Choice, Comment, Profile, Message  # 🔧 ДОБАВЬ сюда Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message  # ✅ без кавычек — это класс модели
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Введите сообщение...'}),
        }

