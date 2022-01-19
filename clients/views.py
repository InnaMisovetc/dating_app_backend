from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from .serializers import ClientSerializer


class ClientCreateView(CreateAPIView):
    permission_classes = [AllowAny]

    queryset = get_user_model().objects.all()
    serializer_class = ClientSerializer
