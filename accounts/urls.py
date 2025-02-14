from django.urls import path
from . import views

urlpatterns = [
    path( 'signup/',  views.signup, name='signup'),
    path('user-view', views.user_list_view, name='user'),
]