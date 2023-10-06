def notifications_to_base(request):
    user = request.user

    if user.is_authenticated:
        unread_notifications_count = user.notification_reciever.filter(read=False).count()
        return {'unread_notifications_count': unread_notifications_count}
    else:
        return {}