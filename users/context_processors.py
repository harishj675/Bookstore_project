from .models import UserProfile, Notifications


def get_user_profile(request):
    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user_id=request.user.id)
        except UserProfile.DoesNotExist:
            pass
    return {'user_profile': user_profile}


def get_notification_count(request):
    notification_list = Notifications.objects.filter(user_id=request.user.id, is_read=False)
    return {'count_of_unread_notifications': len(notification_list)}
