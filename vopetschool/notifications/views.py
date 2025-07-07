from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpRequest
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_protect

from .models import Notification

import json
from typing import Any


@login_required
@require_http_methods(["GET"])
def notifications_api(request: HttpRequest) -> JsonResponse:
    """
    Повертає останні 20 нотифікацій користувача.
    """
    notifications_qs = (
        Notification.objects
        .filter(user=request.user)
        .order_by("-created_at")[:20]
    )

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
@require_http_methods(["POST"])
@csrf_protect
def delete_all_notifications(request: HttpRequest) -> JsonResponse:
    """
    Видаляє всі нотифікації користувача.
    """
    Notification.objects.filter(user=request.user).delete()
    return JsonResponse({"status": "ok"})


@login_required
@require_http_methods(["POST"])
@csrf_protect
def delete_notification(request: HttpRequest) -> JsonResponse:
    """
    Видаляє конкретну нотифікацію за ID.
    """
    try:
        payload: dict[str, Any] = json.loads(request.body)
        notif_id = payload.get("id")

        if not notif_id:
            raise ValidationError("ID нотифікації не передано.")

        deleted_count, _ = Notification.objects.filter(
            id=notif_id,
            user=request.user
        ).delete()

        if deleted_count == 0:
            return JsonResponse({"status": "not_found"}, status=404)

        return JsonResponse({"status": "deleted"})

    except (json.JSONDecodeError, ValidationError) as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=400)
