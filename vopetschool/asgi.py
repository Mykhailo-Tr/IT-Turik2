import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vopetschool.settings")
django.setup()  

from notifications.routing import websocket_urlpatterns
from voting.routing import websocket_urlpatterns as voting_websocket_urlpatterns
from petitions.routing import websocket_urlpatterns as petitions_websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns + 
            voting_websocket_urlpatterns +
            petitions_websocket_urlpatterns
            )
    ),
})
