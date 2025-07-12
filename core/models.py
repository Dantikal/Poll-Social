# models.py
from django.db import models
from django.contrib.auth.models import User

def user_avatar_path(instance, filename):
    return f'avatars/user_{instance.user.id}/{filename}'

class FriendRequest(models.Model):
    from_user = models.ForeignKey(User, related_name='friend_requests_sent', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='friend_requests_received', on_delete=models.CASCADE)
    status = models.CharField(
        max_length=20,
        choices=(
            ('pending', 'Pending'),
            ('accepted', 'Accepted')
        ),
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user.username} ➞ {self.to_user.username} ({self.status})"

class Message(models.Model):
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)  # новое поле для статуса прочитанности

    def __str__(self):
        return f'From {self.sender.username} to {self.recipient.username} at {self.created_at}'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=user_avatar_path, blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    friends = models.ManyToManyField(User, related_name='friends', blank=True)


    def __str__(self):
        return f"{self.user.username}'s profile"


    def __str__(self):
        return f"{self.user.username}'s profile"

class Poll(models.Model):
    question = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_polls', blank=True)

    def __str__(self):
        return self.question

    def total_likes(self):
        return self.likes.count()

class Choice(models.Model):
    poll = models.ForeignKey(Poll, related_name='choices', on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=100)
    votes = models.IntegerField(default=0)

    def __str__(self):
        return self.choice_text

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    poll = models.ForeignKey(Poll, related_name="comments", on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        username = self.user.username if self.user else "Unknown"
        return f'Comment by {username}'

class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'poll')

class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)  # Кому уведомление
    sender = models.ForeignKey(User, related_name='sent_notifications', on_delete=models.CASCADE)  # Кто сделал действие (подписался)
    notification_type = models.CharField(max_length=50)  # Например, 'follow'
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username} from {self.sender.username}"

