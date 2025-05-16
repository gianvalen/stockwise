from django.urls import path
from .views import home_manager, pending_requests, transfer_materials_home, transfer_material

app_name = 'project_management'

urlpatterns = [
    path('home/', home_manager, name='home_manager'),
    path('pending-requests/', pending_requests, name='pending_requests'),
    path('materials/transfer/', transfer_materials_home, name='transfer_materials'),
    path('materials/transfer/<project_id>/<material_id>/', transfer_material, name='transfer_material_form'),
]