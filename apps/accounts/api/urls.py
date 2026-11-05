from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenBlacklistView

urlpatterns = [
    path('signup/', views.CustomRegistrationView.as_view(), name='register-user'),
    path('token/', TokenObtainPairView.as_view(), name='login-user'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token-blacklist'),
    path('me/', views.CustomGetCurrentUserView.as_view(), name='get-current-user'),

]
