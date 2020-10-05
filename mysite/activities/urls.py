from django.conf.urls import url
from .import views
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static

app_name = 'activities'
urlpatterns = [


path('like/',views.LikeView.as_view(),name='like'),
path('bookmark/',views.BookmarkView.as_view(),name='bookmark'),

]