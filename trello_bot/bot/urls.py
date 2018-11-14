from django.urls import path
from . import views
from .views import token

urlpatterns = [
	path(token, views.main, name='main'),
]