from django.urls import re_path
from .consumers import PetitionSupportConsumer, PetitionListConsumer

websocket_urlpatterns = [
    re_path(r'ws/petitions/(?P<petition_id>\d+)/$', PetitionSupportConsumer.as_asgi()),
    re_path(r'ws/petitions/$', PetitionListConsumer.as_asgi()),

]
