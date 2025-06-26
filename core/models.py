from django.db import models
from django.contrib.auth.models import User


# models.py
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.jpg')
    about = models.TextField(blank=True, null=True)  # поле "расскажите о себе"

    def __str__(self):
        return f'{self.user.username} Profile'



# models.py

class Poll(models.Model):
    question = models.CharField(max_length=255)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name='liked_polls', blank=True)  # <-- добавлено

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
        return f'Comment by {self.user.username}'
    
class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    choice = models.ForeignKey(Choice, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'poll')  # Один голос на один опрос



def user_avatar_path(instance, filename):
    return f'avatars/user_{instance.user.id}/{filename}'


