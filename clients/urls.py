from django.urls import path

from .views import ClientCreateView

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [path('create', ClientCreateView.as_view()),
               path('token', TokenObtainPairView.as_view()),
               path('token/refresh', TokenRefreshView.as_view())]
