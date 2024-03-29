from django.urls import path
from .views import *

app_name = 'netizen'

urlpatterns = [
    path('templates/', TemplatesList.as_view(),name='template_list'),

    # path('<str:username>/templates/', UserTemplatesList.as_view(),name='user_templates'),
    path('templates/upload/', TemplateUploadView.as_view(),name='template_upload'),
    path('templates/<id>/', TemplateView.as_view(),name='template_detail'),

    # path('<str:username>/memes/', UserMemesList.as_view(),name='user_memes'),
    path('memes/', MemesList.as_view(),name='meme_list'),
    path('memes/upload/', MemeUploadView.as_view(),name='meme_upload'),
    path('memes/<id>/', MemeView.as_view(),name='meme_detail'),
]