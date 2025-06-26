from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('poll/<int:pk>/', views.poll_detail, name='poll_detail'),
    path('create/', views.create_poll, name='create_poll'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('profile/', views.profile, name='profile'),  # Показываем профиль
    path('profile/edit/', views.profile_edit, name='profile_edit'),  # Редактируем профиль

    path('poll/<int:poll_id>/vote/', views.vote, name='vote'),
    path('poll/<int:poll_id>/like/', views.like_poll, name='like_poll'),
    path('poll/<int:poll_id>/comment/', views.add_comment, name='add_comment'),
    path('user/<str:username>/', views.user_profile, name='user_profile'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)




