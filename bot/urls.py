from django.urls import path
from . import views
from .trello_requests import data

urlpatterns = [
    path(data['token'], views.main, name='main'),
    path('', views.dashboard, name='dashboard'),
]
