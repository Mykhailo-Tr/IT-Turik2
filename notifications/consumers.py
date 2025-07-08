import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Notification
from django.contrib.auth.models import AnonymousUser
from asgiref.sync import sync_to_async

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"] == AnonymousUser():
            await self.close()
        else:
            self.user = self.scope["user"]
            self.group_name = f"user_{self.user.id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
            await self.send_notifications()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    @sync_to_async
    def get_user_notifications(self):
        return list(Notification.objects.filter(user=self.user).order_by("-created_at")[:20])

    async def send_notifications(self):
        notifications = await self.get_user_notifications()
        data = [
            {
                "id": n.id,
                "message": n.message,
                "link": n.link or "#",
            }
            for n in notifications
        ]
        await self.send(text_data=json.dumps({"notifications": data}))

    async def notify(self, event):
        await self.send_notifications()
