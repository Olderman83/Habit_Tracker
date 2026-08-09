from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.contrib.auth import views as auth_views
from .views import UserRegistrationView, EmailVerificationView, UserProfileView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('verify/<str:token>/', EmailVerificationView.as_view(), name='verify-email'),
    path('profile/', UserProfileView.as_view(), name='profile'),

    # JWT
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Password reset (Django built-in)
    path('password-reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(),
         name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
