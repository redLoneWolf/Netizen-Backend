from django.urls import path
from .views import *

app_name = 'reports'

urlpatterns = [
    path('content/', ContentReportCreateView.as_view(),name='report_content'),
    path('user/', UserReportCreateView.as_view(),name='report_user'),



]