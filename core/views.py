from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.forms import modelformset_factory
from django.contrib.auth.models import User
from django.db.models import Q, Max, Count
from . import models

from .models import Poll, Choice, Comment, Vote, Profile, FriendRequest, Notification, Message
from .forms import PollForm, ChoiceFormSet, CommentForm, UserRegisterForm, ProfileUpdateForm


@login_required(login_url='login')
def home(request):
    polls = Poll.objects.all().prefetch_related('comments', 'choices', 'likes').order_by('-created_at')
    user_votes = Vote.objects.filter(user=request.user)
    votes_dict = {vote.poll.id: vote.choice.id for vote in user_votes}
    comment_form = CommentForm()
    return render(request, 'core/home.html', {
        'polls': polls,
        'comment_form': comment_form,
        'user_votes': votes_dict,
    })


def create_poll(request):
    ChoiceFormSetLocal = modelformset_factory(Choice, fields=('choice_text',), extra=4, can_delete=False)

    if request.method == 'POST':
        poll_form = PollForm(request.POST)
        formset = ChoiceFormSetLocal(request.POST, queryset=Choice.objects.none())

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
        formset = ChoiceFormSetLocal(queryset=Choice.objects.none())

    return render(request, 'core/create_poll.html', {
        'poll_form': poll_form,
        'formset': formset,
    })


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


@require_POST
@login_required
def vote(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    if Vote.objects.filter(user=request.user, poll=poll).exists():
        messages.error(request, "Вы уже голосовали в этом опросе.")
        return redirect('home')

    choice_id = request.POST.get('choice')
    if choice_id:
        try:
            selected_choice = poll.choices.get(id=choice_id)
            selected_choice.votes += 1
            selected_choice.save()
            Vote.objects.create(user=request.user, poll=poll, choice=selected_choice)
        except Choice.DoesNotExist:
            messages.error(request, "Выбранный вариант не существует.")
    return redirect('home')


def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # Сигнал создаст Profile
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})


@login_required
def profile(request):
    """Личный профиль текущего пользователя"""
    user_polls = Poll.objects.filter(author=request.user).order_by('-created_at')

    return render(request, 'core/profile.html', {
        'user': request.user,
        'user_polls': user_polls,
    })


def logout_view(request):
    logout(request)
    return redirect('login')


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


@login_required
def like_poll(request, poll_id):
    poll = get_object_or_404(Poll, id=poll_id)
    if request.user in poll.likes.all():
        poll.likes.remove(request.user)
    else:
        poll.likes.add(request.user)
    return redirect(request.META.get('HTTP_REFERER', 'home'))


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


@login_required
def profile_edit(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=profile, user=request.user)
    return render(request, 'core/profile_edit.html', {'form': form})


def user_profile(request, username):
    """Профиль другого пользователя"""
    user_obj = get_object_or_404(User, username=username)
    profile = user_obj.profile
    polls = Poll.objects.filter(author=user_obj).order_by('-created_at')

    # Проверка на входящего/исходящего друга
    incoming_request = None
    outgoing_request = None
    are_friends = False

    if request.user.is_authenticated:
        incoming_request = FriendRequest.objects.filter(from_user=user_obj, to_user=request.user).first()
        outgoing_request = FriendRequest.objects.filter(from_user=request.user, to_user=user_obj).first()
        are_friends = user_obj in request.user.profile.friends.all()

    context = {
        'profile_user': user_obj,
        'profile': profile,
        'user_polls': polls,
        'incoming_request': incoming_request,
        'outgoing_request': outgoing_request,
        'are_friends': are_friends,
    }

    return render(request, 'core/user_profile.html', context)


@login_required
def send_friend_request(request, username):
    to_user = get_object_or_404(User, username=username)
    from_user = request.user

    if to_user == from_user:
        messages.error(request, "Нельзя отправить заявку самому себе.")
        return redirect('user_profile', username=username)

    if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
        messages.info(request, "Заявка уже была отправлена.")
    elif to_user.profile.friends.filter(id=from_user.id).exists():
        messages.info(request, "Вы уже друзья.")
    else:
        FriendRequest.objects.create(from_user=from_user, to_user=to_user)
        messages.success(request, "Заявка в друзья отправлена.")

    return redirect('user_profile', username=username)


@login_required
def accept_friend_request_view(request, request_id):
    friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)

    # Добавляем друг друга в друзья
    friend_request.from_user.profile.friends.add(friend_request.to_user)
    friend_request.to_user.profile.friends.add(friend_request.from_user)

    # Удаляем заявку
    friend_request.delete()

    return redirect('friends_list')


@login_required
def friend_requests_view(request):
    incoming_requests = request.user.friend_requests_received.all()
    return render(request, 'core/friend_requests.html', {'incoming_requests': incoming_requests})


@login_required
def chat_list(request):
    # Получаем всех друзей текущего пользователя
    friends = request.user.profile.friends.all()

    # Получаем время последних сообщений между текущим пользователем и каждым другом
    last_messages = Message.objects.filter(
        Q(sender=request.user, recipient__in=friends) |
        Q(sender__in=friends, recipient=request.user)
    ).values('sender', 'recipient').annotate(last_time=Max('created_at')).order_by('-last_time')

    # Формируем множество пользователей из последних сообщений (исключая себя)
    chat_users = set()
    for m in last_messages:
        chat_users.add(m['sender'])
        chat_users.add(m['recipient'])
    chat_users.discard(request.user.id)

    # Получаем объекты User
    users = User.objects.filter(id__in=chat_users)

    # Подсчитываем количество непрочитанных сообщений от каждого пользователя
    unread_counts = Message.objects.filter(
        sender__in=users,
        recipient=request.user,
        is_read=False
    ).values('sender').annotate(unread_count=Count('id'))

    # Преобразуем в словарь { sender_id: unread_count }
    unread_dict = {item['sender']: item['unread_count'] for item in unread_counts}

    return render(request, 'core/chat_list.html', {
        'users': users,
        'unread_dict': unread_dict,
    })


@login_required
def chat_view(request, username):
    user = request.user
    try:
        other_user = User.objects.get(username=username)
    except User.DoesNotExist:
        messages.error(request, "Пользователь не найден.")
        return redirect('home')

    if other_user not in user.profile.friends.all():
        messages.error(request, "Вы не можете писать этому пользователю, вы не друзья.")
        return redirect('home')

    # Помечаем все непрочитанные сообщения от other_user к user как прочитанные
    Message.objects.filter(sender=other_user, recipient=user, is_read=False).update(is_read=True)

    chat_messages = Message.objects.filter(
        (Q(sender=user) & Q(recipient=other_user)) |
        (Q(sender=other_user) & Q(recipient=user))
    ).order_by('created_at')

    if request.method == "POST":
        text = request.POST.get("text")
        if text:
            Message.objects.create(sender=user, recipient=other_user, text=text)
            return redirect('chat_view', username=other_user.username)

    return render(request, 'core/chat.html', {
        'chat_messages': chat_messages,
        'other_user': other_user,
        'user': user,
    })


@login_required
def profile_view(request):
    user_profile = request.user.profile
    user_polls = Poll.objects.filter(author=request.user)  # опросы текущего пользователя

    return render(request, 'core/profile.html', {
        'profile_user': request.user,
        'profile': user_profile,
        'user_polls': user_polls,
    })

@login_required
def friends_list_view(request):
    user_profile = request.user.profile
    friends = user_profile.friends.all()
    return render(request, 'core/friends_list.html', {'friends': friends})


@login_required
def clear_chat(request, username):
    other_user = get_object_or_404(User, username=username)

    # Удаляем все сообщения между текущим пользователем и другим пользователем
    Message.objects.filter(
        sender=request.user, recipient=other_user
    ).delete()
    Message.objects.filter(
        sender=other_user, recipient=request.user
    ).delete()

    return redirect('chat_view', username=username)


@login_required
def notifications_view(request):
    notifications = request.user.notifications.order_by('-created_at')

    # Можно сразу отметить все как прочитанные
    notifications.filter(is_read=False).update(is_read=True)

    return render(request, 'core/notifications.html', {'notifications': notifications})
