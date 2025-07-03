from django.urls import path
from .views import (
    PetitionListView,
    petition_detail_view,
    support_petition_view,
    PetitionCreateView,
)

urlpatterns = [
    path("", PetitionListView.as_view(), name="petition_list"),
    path("create/", PetitionCreateView.as_view(), name="petition_create"),
    path("<int:pk>/", petition_detail_view, name="petition_detail"),
    path("<int:pk>/support/", support_petition_view, name="support_petition"),
]