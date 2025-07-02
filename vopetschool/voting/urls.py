from django.urls import path
from .views import vote_detail_view, VoteListView

urlpatterns = [
    path("", VoteListView.as_view(), name="vote_list"),
    path("<int:pk>/", vote_detail_view, name="vote_detail"),
]