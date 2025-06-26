from django import forms
from .models import Poll, Choice, Comment
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.forms import modelformset_factory


class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ['question']

class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['choice_text']

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

from django import forms
from django.forms import inlineformset_factory
from .models import Poll, Choice

class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ['question']


from django.forms import modelformset_factory
from .models import Choice
from .forms import ChoiceForm

ChoiceFormSet = modelformset_factory(
    Choice,
    form=ChoiceForm,
    extra=3,  # показываем 3 пустые формы
    max_num=100,
    can_delete=False,
)



# forms.py
from django import forms
from .models import Profile

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']


# forms.py
from django import forms
from .models import Profile
from django.contrib.auth.models import User

class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = Profile
        fields = ['avatar', 'about']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['email'].initial = user.email

    def save(self, commit=True):
        profile = super().save(commit=False)
        user = profile.user
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            profile.save()
        return profile
    
    from django import forms
from .models import Profile

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



