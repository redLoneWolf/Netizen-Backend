from django.urls import path
from .views import *

app_name = 'comments'

urlpatterns = [
    path('comment/', CommentCreateView.as_view(),name='comment_create'),
    path('u/<uuid:id>/', CommentUpdateView.as_view(),name='comment_update'),
    path('d/<uuid:id>/', CommentDeleteView.as_view(),name='comment_delete'),
    path('l/', CommentList.as_view(),name='comment_list'),


]