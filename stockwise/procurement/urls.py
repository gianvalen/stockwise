from django.urls import path
from .views import home_procurement, projects_list, project_detail

app_name = 'procurement'

urlpatterns = [
    path('home/', home_procurement, name='home_procurement'),
    path('projects/', projects_list, name='projects_list'),
    path('projects/<str:project_id>/', project_detail, name='project_detail'),
]