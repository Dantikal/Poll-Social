from django import template
from core.models import FriendRequest
from django.db.models import Q

register = template.Library()

@register.filter
def has_sent_request(user, other_user):
    if not user.is_authenticated:
        return False
    return FriendRequest.objects.filter(from_user=user, to_user=other_user).exists()

@register.filter
def has_received_request(user, other_user):
    if not user.is_authenticated:
        return False
    return FriendRequest.objects.filter(from_user=other_user, to_user=user).exists()

@register.filter
def is_friend(user, other_user):
    if not user.is_authenticated:
        return False
    return user.profile.friends.filter(id=other_user.id).exists()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)
