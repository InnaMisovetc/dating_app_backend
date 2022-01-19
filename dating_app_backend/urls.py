from django.contrib import admin
from django.urls import path, include

from clients.views import ClientsListView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/clients/', include('clients.urls')),
    path('api/list', ClientsListView.as_view()),
]
