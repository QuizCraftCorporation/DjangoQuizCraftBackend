from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from authorization.views import RegisterView, UserInfoView, LogoutView, LogoutAllView, RefreshView

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name="sign_up"),
    path('user-me/', UserInfoView.as_view(), name='user_info'),
    path('logout/', LogoutView.as_view(), name='auth_logout'),
    path('logout_all/', LogoutAllView.as_view(), name='auth_logout_all'),
]
