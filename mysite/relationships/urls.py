from django.conf.urls import url

from django.urls import path,include,reverse_lazy
from django.conf import settings
from django.conf.urls.static import static

from .views import (

    FollowView,
    BlockView,

) 



app_name = 'relationships'
urlpatterns = [

    path('follow/',FollowView.as_view(),name='follow'),
    path('block/',BlockView.as_view(),name='block'),

]