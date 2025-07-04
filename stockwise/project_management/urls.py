from django.urls import path
from .views import home_manager, pending_requests, transfer_materials_home, transfer_material, pending_offers_proj, projects_list, project_detail, request_material

app_name = 'project_management'

urlpatterns = [
    path('home/', home_manager, name='home_manager'),
    path('projects/', projects_list, name='projects_list'),
    path('projects/<str:project_id>/', project_detail, name='project_detail'),
    path('projects/<str:project_id>/request-material/', request_material, name='purchase_request_create'),
    path('pending-requests/', pending_requests, name='pending_requests'),
    path('materials/transfer/', transfer_materials_home, name='transfer_materials'),
    path('materials/transfer/<project_id>/<material_id>/', transfer_material, name='transfer_material_form'),
    path('pending-offers-proj/', pending_offers_proj, name='pending_offers_proj'),
]