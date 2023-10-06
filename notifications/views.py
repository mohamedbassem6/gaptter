from django.shortcuts import render
from django.http import JsonResponse
import json

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect

@login_required
@csrf_protect
def notifications_get(request):
    if request.method == 'POST':
        user = request.user

        notifications = user.notification_reciever.order_by('-date')

        notifications_list = []

        for notification in notifications:
            if notification.type == 'like' or notification.type == 'reGapt':
                data = {
                    'type': notification.type,
                    'sender_name': notification.sender.profile.name,
                    'sender_username': notification.sender.username,
                    'sender_profile_image': notification.sender.profile.profile_image.url,
                    'film': notification.activity.gapt.film.title,
                    'gapt_id': notification.activity.gapt.id,
                    'time': notification.when(),
                    'read': notification.read,
                }

            elif notification.type == 'follow':
                data = {
                    'type': notification.type,
                    'sender_name': notification.sender.profile.name,
                    'sender_username': notification.sender.username,
                    'sender_profile_image': notification.sender.profile.profile_image.url,
                    'time': notification.when(),
                    'read': notification.read,
                }

            notifications_list.append(data)

        notifications.update(read=True)

        return JsonResponse({'status': 'success', 'notifications': notifications_list})
    else:
        return JsonResponse({'status': 'error'})