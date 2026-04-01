from django.urls import path
from .import views

urlpatterns = [
    path('', views.index, name='index'),  # This will be the home page of the app
]