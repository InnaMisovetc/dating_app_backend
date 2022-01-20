from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models.expressions import RawSQL
from django_filters import rest_framework as filters
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from dating_app_backend import settings
from .filters import ClientFilter
from .models import Client
from .serializers import ClientSerializer


class ClientCreateView(CreateAPIView):
    permission_classes = [AllowAny]

    queryset = get_user_model().objects.all()
    serializer_class = ClientSerializer


class ClientsListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Client.objects.all()
    serializer_class = ClientSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ClientFilter

    def get_queryset(self):
        max_distance = self.request.query_params.get('distance')
        if max_distance is None:
            return Client.objects.all()
        else:
            return self.get_clients_within_distance(float(max_distance))

    def get_clients_within_distance(self, max_distance):
        origin_lat = self.request.user.latitude
        origin_long = self.request.user.longitude
        gcd = "6371 * acos(least(greatest(\
        cos(radians(%s)) * cos(radians(latitude)) \
        * cos(radians(longitude) - radians(%s)) + \
        sin(radians(%s)) * sin(radians(latitude)) \
        , -1), 1))"
        distance_raw_sql = RawSQL(gcd, (origin_lat, origin_long, origin_lat))
        return Client.objects.all().annotate(distance=distance_raw_sql).filter(distance__lt=max_distance)


class MatchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, client_id):
        liked_client = Client.objects.get(id=client_id)
        current_client = request.user

        if liked_client == current_client:
            return Response('User is not allowed match with self', status=status.HTTP_403_FORBIDDEN)

        liked_client.liked.add(current_client)

        if liked_client in current_client.liked.all():
            self.send_match_notification(liked_client, current_client)
            self.send_match_notification(current_client, liked_client)
            return Response(f'Match: {liked_client} and {current_client}', status=status.HTTP_200_OK)

        return Response(status=status.HTTP_200_OK)

    @staticmethod
    def send_match_notification(liked_client, target_client, topic='Match!'):
        send_mail(
            topic,
            f'{liked_client.first_name} liked you! Email of the participant {liked_client.email}!',
            settings.EMAIL_HOST_USER,
            [target_client.email],
            fail_silently=False,
        )
