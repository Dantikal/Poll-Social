from django.contrib import admin
from .models import Poll, Choice, Comment, Profile

admin.site.register(Poll)
admin.site.register(Choice)
admin.site.register(Comment)
admin.site.register(Profile)
