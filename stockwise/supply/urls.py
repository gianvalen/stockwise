from django.urls import path
from .views import home_supplier, requests_list, requests_detail

app_name = 'supply'

urlpatterns = [
    path('home/', home_supplier, name='home_supplier'),
    path('requests/', requests_list, name='requests_list'),
    path('requests/<str:pr_id>/', requests_detail, name='requests_detail'),
]