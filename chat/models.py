from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Conversation(models.Model):
    users = models.ManyToManyField(User, blank=False)
    # messages = models.ManyToManyField(Message, blank=True)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return str([user.username for user in self.users.all()])

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, blank=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)
    content = models.TextField(blank=False)
    seen = models.BooleanField(default=False)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{ self.sender.profile }: { self.date }'