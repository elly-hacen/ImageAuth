from django.urls import path
from . import views

app_name = 'forgery_detection'

urlpatterns = [
    path('', views.home, name='home'),
] 
