from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import ClientCreateView, MatchView

urlpatterns = [path('create', ClientCreateView.as_view()),
               path('token', TokenObtainPairView.as_view()),
               path('token/refresh', TokenRefreshView.as_view()),
               path('<int:client_id>/match', MatchView.as_view())]
