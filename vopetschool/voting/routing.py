from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/votes/<int:vote_id>/", consumers.VoteStatsConsumer.as_asgi()),
]