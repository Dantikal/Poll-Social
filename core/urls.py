from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),

    # Опросы
    path('poll/<int:pk>/', views.poll_detail, name='poll_detail'),
    path('create/', views.create_poll, name='create_poll'),
    path('poll/<int:poll_id>/vote/', views.vote, name='vote'),
    path('poll/<int:poll_id>/like/', views.like_poll, name='like_poll'),
    path('poll/<int:poll_id>/comment/', views.add_comment, name='add_comment'),

    # Аутентификация
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Профиль пользователя
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),

    # Друзья
    path('friends/', views.friends_list_view, name='friends_list'),
    path('send_friend_request/<str:username>/', views.send_friend_request, name='send_friend_request'),
    path('accept_friend_request/<int:request_id>/', views.accept_friend_request_view, name='accept_friend_request'),
    path('friend-requests/', views.friend_requests_view, name='friend_requests'),

    # Чат
    path('chat/', views.chat_list, name='chat_list'),
    path('chat/<str:username>/', views.chat_view, name='chat_view'),
    path('chat/<str:username>/clear/', views.clear_chat, name='clear_chat'),
    path('notifications/', views.notifications_view, name='notifications'),



]

# Подключение медиа-файлов в режиме отладки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
