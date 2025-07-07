import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Petition
from .views import calculate_petition_support

class PetitionSupportConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.petition_id = self.scope["url_route"]["kwargs"]["petition_id"]
        self.group_name = f"petition_{self.petition_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def petition_support_update(self, event):
        await self.send(text_data=json.dumps(event["data"]))



class PetitionListConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("petitions", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("petitions", self.channel_name)

    async def receive(self, text_data):
        # Опціонально: не обов'язково обробляти вхідні дані
        pass

    async def petition_support_updated(self, event):
        await self.send(text_data=json.dumps({
            "petition_id": event["petition_id"],
            "supporters_count": event["supporters_count"],
            "support_percent": event["support_percent"],
        }))