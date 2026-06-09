from .models import Notification

def notifications_globales(request):
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(
            destinataire=request.user
        ).order_by('-date')[:8]
        non_lues = Notification.objects.filter(
            destinataire=request.user, lue=False
        ).count()
        return {
            'notifications_global': notifications,
            'non_lues_global': non_lues,
        }
    return {
        'notifications_global': [],
        'non_lues_global': 0,
    }