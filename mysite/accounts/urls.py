from django.conf.urls import url

from django.urls import path,include,reverse_lazy
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    UserCreateAPIView,
    UserListView,
    UserDetailView,
  
    PasswordChangeView,
    PasswordResetView,
    PasswordResetConfirmView,
    PasswordResetDoneView,
    GoogleRegisterView,
    GoogleLoginDoneView,
    GoogleLoginView,
    MyProfileView,

) 

# register_converter(converters.FourDigitYearConverter, 'yyyy')
from rest_framework_simplejwt import views as jwt_views


app_name = 'accounts'
urlpatterns = [
    path('users/', UserListView.as_view(),name='users_list'),

    path('users/<str:username>/', UserDetailView.as_view(),name='users_detail'),
    path('profile/', MyProfileView.as_view(),name='profile'),

  

    path('login/', GoogleLoginDoneView.as_view(),name='google_login'),
    path('google/',GoogleRegisterView.as_view(),name='google_register'),
    path('google/login/',GoogleLoginView.as_view(),name='google_login2'),
    path('register/', UserCreateAPIView.as_view(),name='register'),
    
    path('password/',PasswordChangeView.as_view(),name='change_password'),
    path('reset/', PasswordResetView.as_view(),name='password_reset'),
    path('reset/confirm/<uidb64>/<token>',PasswordResetConfirmView.as_view(),name='password_reset_confirm'),
    path('reset/complete/',PasswordResetDoneView.as_view(),name='password_reset_complete'),


    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    
]