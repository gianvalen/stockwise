from django.urls import path
from .views import home_supplier, requests_list, requests_detail, offer_material

app_name = 'supply'

urlpatterns = [
    path('home/', home_supplier, name='home_supplier'),
    path('requests/', requests_list, name='requests_list'),
    path('requests/<str:pr_id>/', requests_detail, name='requests_detail'),
    path('requests/<str:pr_id>/<str:material_id>/offer/', offer_material, name='offer_material'),
]