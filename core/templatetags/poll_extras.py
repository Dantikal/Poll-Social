# core/templatetags/poll_extras.py
from django import template
from core.models import Vote

register = template.Library()

@register.filter
def has_voted(user, poll):
    if not user.is_authenticated:
        return False
    return Vote.objects.filter(user=user, poll=poll).exists()

@register.filter
def sum_votes(choices):
    """Возвращает сумму голосов по всем вариантам."""
    return sum(choice.votes for choice in choices)

@register.filter
def percentage(votes, total):
    """Вычисляет процент голосов от общего количества."""
    if total == 0:
        return 0
    return round((votes / total) * 100, 1)
