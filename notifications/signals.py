from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver

from core.models import LikeLog, ReGaptLog
from users.models import FollowLog
from notifications.models import ActivityNotification

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@receiver(post_save, sender=FollowLog)
@receiver(post_save, sender=ReGaptLog)
@receiver(post_save, sender=LikeLog)
def notfication_broadcast(sender, instance, created, **kwargs):
    if created:
        notification = ActivityNotification.objects.create(activity=instance)

        channel_layer = get_channel_layer()
        group_name = notification.reciever.username

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_notification',
            }
        )


@receiver(pre_delete, sender=FollowLog)
@receiver(pre_delete, sender=ReGaptLog)
@receiver(pre_delete, sender=LikeLog)
def notification_cleanup(sender, instance, **kwargs):
    if sender is LikeLog:
        type = 'like'
    elif sender is ReGaptLog:
        type = 'reGapt'
    elif sender is FollowLog:
        type = 'follow'

    notification = ActivityNotification.objects.get(object_id=instance.id, type=type)
    notification.delete()