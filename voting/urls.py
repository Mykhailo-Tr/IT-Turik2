from django.urls import path
from .views import vote_detail_view, VoteListView, VoteCreateView, vote_delete_view,

urlpatterns = [
    path("", VoteListView.as_view(), name="vote_list"),
    path("<int:pk>/", vote_detail_view, name="vote_detail"),
    path("create/", VoteCreateView.as_view(), name="vote_create"),
    path("<int:pk>/delete/", vote_delete_view, name="vote_delete"),

]