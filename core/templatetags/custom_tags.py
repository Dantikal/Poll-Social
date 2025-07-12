from django import template
from core.models import Message  # поправь под свою модель

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def unread_messages_count(user):
    if user.is_authenticated:
        return Message.objects.filter(recipient=user, is_read=False).count()
    return 0
