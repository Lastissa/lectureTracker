from django.urls import path
from api_version_2 import views

urlpatterns = [
    path('', views.Home.as_view())
]