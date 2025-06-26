from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .models import Poll, Choice, Comment, Vote
from .forms import PollForm, ChoiceFormSet, CommentForm, UserRegisterForm
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProfileUpdateForm




# ✅ Только одна функция home — с login_required и polls
@login_required(login_url='login')
def home(request):
    polls = Poll.objects.all().prefetch_related('comments', 'choices', 'likes').order_by('-created_at')

    # Получаем голоса пользователя для всех опросов
    user_votes = Vote.objects.filter(user=request.user)
    votes_dict = {vote.poll.id: vote.choice.id for vote in user_votes}

    comment_form = CommentForm()
    return render(request, 'core/home.html', {
        'polls': polls,
        'comment_form': comment_form,
        'user_votes': votes_dict,
    })

# ✅ Создание опроса
from django.shortcuts import render, redirect
from django.forms import modelformset_factory
from .forms import PollForm
from .models import Poll, Choice

def create_poll(request):
    ChoiceFormSet = modelformset_factory(Choice, fields=('choice_text',), extra=4, can_delete=False)

    if request.method == 'POST':
        poll_form = PollForm(request.POST)
        formset = ChoiceFormSet(request.POST, queryset=Choice.objects.none())  # пустой набор, т.к. новых Choice ещё нет

        if poll_form.is_valid() and formset.is_valid():
            poll = poll_form.save(commit=False)
            poll.author = request.user
            poll.save()

            choices = formset.save(commit=False)
            for choice in choices:
                choice.poll = poll
                choice.save()
            return redirect('home')
    else:
        poll_form = PollForm()
        formset = ChoiceFormSet(queryset=Choice.objects.none())  # только пустые формы

    return render(request, 'core/create_poll.html', {
        'poll_form': poll_form,
        'formset': formset,
    })




# ✅ Детали опроса + комментарии
def poll_detail(request, pk):
    poll = get_object_or_404(Poll, pk=pk)
    comment_form = CommentForm()
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user if request.user.is_authenticated else None
            comment.poll = poll
            comment.save()
            return redirect('poll_detail', pk=pk)
    return render(request, 'core/poll_detail.html', {'poll': poll, 'form': comment_form})

# ✅ Голосование — 1 раз на пользователя
@require_POST
@login_required
def vote(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    if Vote.objects.filter(user=request.user, poll=poll).exists():
        messages.error(request, "Вы уже голосовали в этом опросе.")
        return redirect('home')  # изменено с poll_detail на home

    choice_id = request.POST.get('choice')
    if choice_id:
        try:
            selected_choice = poll.choices.get(id=choice_id)
            selected_choice.votes += 1
            selected_choice.save()
            Vote.objects.create(user=request.user, poll=poll, choice=selected_choice)
        except Choice.DoesNotExist:
            messages.error(request, "Выбранный вариант не существует.")
    return redirect('home')  # изменено с poll_detail на home

# ✅ Регистрация
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})

# ✅ Профиль
@login_required
def profile(request):
    user_polls = Poll.objects.filter(author=request.user).order_by('-created_at')
    return render(request, 'core/profile.html', {
        'user': request.user,
        'user_polls': user_polls
    })

# ✅ Выход из аккаунта
def logout_view(request):
    logout(request)
    return redirect('login')

# ✅ Логин
def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Неверные данные, попробуйте еще раз.")
    else:
        if 'next' in request.GET:
            messages.warning(request, "Для доступа к главной странице нужно войти в аккаунт.")
        form = AuthenticationForm()
    return render(request, 'core/login.html', {'form': form})

# ✅ Лайки опроса
@login_required
def like_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)

    if request.user in poll.likes.all():
        poll.likes.remove(request.user)
    else:
        poll.likes.add(request.user)

    # Возвращаем обратно на страницу, откуда пришёл запрос
    return redirect(request.META.get('HTTP_REFERER', 'home'))

# ✅ Добавление комментария
@login_required
@require_POST
def add_comment(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.poll = poll
        comment.save()
    return redirect(request.META.get('HTTP_REFERER', 'home'))

# signals.py
Profile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    instance.profile.save()

# views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProfileUpdateForm

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile')  # замените на ваш URL
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'users/edit_profile.html', {'form': form})


# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import ProfileUpdateForm

@login_required
def profile_view(request):
    return render(request, 'profile.html')



@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
        else:
            print(form.errors)
    else:
        form = ProfileUpdateForm(instance=profile, user=request.user)
    return render(request, 'core/profile_edit.html', {'form': form})


def user_profile(request, username):
    user_obj = get_object_or_404(User, username=username)
    profile = user_obj.profile
    polls = Poll.objects.filter(author=user_obj).order_by('-created_at')
    return render(request, 'core/user_profile.html', {
        'profile_user': user_obj,
        'profile': profile,
        'user_polls': polls
    })






