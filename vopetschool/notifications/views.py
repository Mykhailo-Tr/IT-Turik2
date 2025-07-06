# notifications/views.py
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
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


@csrf_exempt
@require_POST
@login_required
def delete_notification(request):
    try:
        data = json.loads(request.body)
        notif_id = data.get("id")
        if notif_id:
            Notification.objects.filter(id=notif_id, user=request.user).delete()
            return JsonResponse({"status": "deleted"})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)

    return JsonResponse({"status": "no_id_provided"}, status=400)

