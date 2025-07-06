# notifications/views.py
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification

@login_required
def notifications_api(request):
    user = request.user
    # Отримуємо всі нотифікації для користувача, найсвіжіші зверху
    notifications_qs = Notification.objects.filter(user=user).order_by('-created_at')[:20]
    notifications = [
        {
            "id": n.id,
            "message": n.message,
            "link": n.link or "#",
        }
        for n in notifications_qs
    ]
    return JsonResponse({"notifications": notifications})

@login_required
def delete_notifications(request):
    # Видаляємо всі нотифікації для користувача (можна розширити, наприклад, за id)
    Notification.objects.filter(user=request.user).delete()
    return JsonResponse({"status": "ok"})

