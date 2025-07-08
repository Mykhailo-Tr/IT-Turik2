import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import VoteOption, Vote
from asgiref.sync import sync_to_async
from django.db.models import Count

class VoteStatsConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.vote_id = self.scope["url_route"]["kwargs"]["vote_id"]
        self.group_name = f"vote_{self.vote_id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        await self.send_vote_stats()  # Надіслати початкові дані

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        # необов'язково — можна викликати вручну `send_vote_stats` з views при новому голосуванні
        await self.send_vote_stats()

    async def vote_update(self, event):
        await self.send_vote_stats()

    async def send_vote_stats(self):
        data = await self.get_vote_stats()
        await self.send(text_data=json.dumps(data))

    @sync_to_async
    def get_vote_stats(self):
        vote = Vote.objects.get(pk=self.vote_id)
        options = VoteOption.objects.filter(vote=vote).annotate(vote_count=Count("answers"))
        total_votes = sum(o.vote_count for o in options)

        return {
            "total_votes": total_votes,
            "options": [
                {
                    "id": o.id,
                    "text": o.text,
                    "count": o.vote_count,
                    "percent": round((o.vote_count / total_votes) * 100) if total_votes else 0,
                }
                for o in options
            ],
        }