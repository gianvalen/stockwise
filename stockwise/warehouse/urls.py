from django.urls import path
from .views import home_warehouse, projects_list, project_detail, update_material_quantity

app_name = 'warehouse'

urlpatterns = [
    path('home/', home_warehouse, name='home_warehouse'),
    path('projects/', projects_list, name='projects_list'),
    path('projects/<str:project_id>/', project_detail, name='project_detail'),
    path('projects/<str:project_id>/<str:material_id>/update/', update_material_quantity, name='update_material'),
]