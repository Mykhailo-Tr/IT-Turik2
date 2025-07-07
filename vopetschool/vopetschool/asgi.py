import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vopetschool.settings")
django.setup()  # 🔧 Обов’язково до будь-яких імпортів моделей/routing

from notifications.routing import websocket_urlpatterns  # ✅ Тепер безпечно

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
