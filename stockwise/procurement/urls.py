from django.urls import path
from .views import home_procurement, projects_list, project_detail, request_material

app_name = 'procurement'

urlpatterns = [
    path('home/', home_procurement, name='home_procurement'),
    path('projects/', projects_list, name='projects_list'),
    path('projects/<str:project_id>/', project_detail, name='project_detail'),
    path('projects/<str:project_id>/request-material/', request_material, name='purchase_request_create'),

]