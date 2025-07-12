from django.contrib import admin
from .models import Poll, Choice, Comment, Profile
from .models import FriendRequest

admin.site.register(Poll)
admin.site.register(Choice)
admin.site.register(Comment)
admin.site.register(Profile)
admin.site.register(FriendRequest)

