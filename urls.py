from django.urls import path, include
from django.contrib.auth.decorators import login_required

from . import views

app_name = 'system_network'

urlpatterns = [
    path('list/', views.DeviceListView.as_view(), name='device_list'),
    path('autoconnect/<str:action>/<str:uuid>/', views.DeviceAutoConnectView.as_view(), name='autoconnect'),
    path('ipv4/edit/<str:name>/<str:uuid>/', views.Ipv4EditView.as_view(), name='ipv4_edit'),
]
