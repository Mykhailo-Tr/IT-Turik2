from django.urls import path
from .views import (
    PetitionListView,
    petition_detail_view,
    support_petition_view,
    PetitionCreateView,
    delete_petition_view,
    set_petition_status,
    add_comment_view,
    edit_comment_view,
    delete_comment_view,
   
)

urlpatterns = [
    path("", PetitionListView.as_view(), name="petition_list"),
    path("create/", PetitionCreateView.as_view(), name="petition_create"),
    path("<int:pk>/delete/", delete_petition_view, name="petition_delete"),
    path("<int:pk>/", petition_detail_view, name="petition_detail"),
    path("<int:pk>/comment/add/", add_comment_view, name="add_comment"),
    path("<int:petition_pk>/comment/<int:comment_pk>/edit/", edit_comment_view, name="edit_comment"),
    path("<int:petition_pk>/comment/<int:comment_pk>/delete/", delete_comment_view, name="delete_comment"),
    path("<int:pk>/support/", support_petition_view, name="support_petition"),
    path("<int:pk>/status/", set_petition_status, name="petition_set_status")

]