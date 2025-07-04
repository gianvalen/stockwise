from django.urls import path
from .views import register, login_view, logout_view

app_name = 'user_management'

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('login', login_view, name= 'login'),
    path('logout/', logout_view, name='logout'),
]