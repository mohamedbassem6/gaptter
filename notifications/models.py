from collections.abc import Iterable
from django.db import models
from django.utils import timezone
import math

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django.contrib.auth.models import User
from core.models import LikeLog

# Create your models here.
class ActivityNotification(models.Model):
    read = models.BooleanField(default=False)
    type = models.TextField(blank=True)
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    activity = GenericForeignKey("content_type", "object_id")

    reciever = models.ForeignKey(User, related_name='notification_reciever', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, related_name='notification_sender', on_delete=models.CASCADE)
    date = models.DateTimeField(blank=True)

    def when(self):
        now = timezone.now()

        datePosted = self.date

        diff = now - datePosted

        if diff.days == 0 and diff.seconds >= 0 and diff.seconds < 60:
            seconds = diff.seconds

            return str(seconds) + "s"

        if diff.days == 0 and diff.seconds >= 60 and diff.seconds < 3600:
            minutes = math.floor(diff.seconds / 60)

            return str(minutes) + "m"

        if diff.days == 0 and diff.seconds >= 3600 and diff.seconds < 86400:
            hours = math.floor(diff.seconds / 3600)

            return str(hours) + "h"

        # 1 day to 30 days
        if diff.days >= 1 and diff.days < 7:
            days = diff.days

            return str(days) + "d"

        return str(int(diff.days / 7)) + "w"

    def save(self, *args, **kwargs):
        self.date = self.activity.date

        if str(self.content_type) == 'core | like log':
            self.reciever = self.activity.gapt.user
            self.sender = self.activity.user
            self.type = 'like'
        elif str(self.content_type) == 'core | re gapt log':
            self.reciever = self.activity.gapt.user
            self.sender = self.activity.user
            self.type = 'reGapt'
        elif str(self.content_type) == 'users | follow log':
            self.reciever = self.activity.followee.user
            self.sender = self.activity.follower.user
            self.type = 'follow'

        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]