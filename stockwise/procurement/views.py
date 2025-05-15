from django.shortcuts import render, get_object_or_404
from stock_management.models import Project, ProjectInventory, InventoryMaterial

def home_procurement(request):
    return render(request, 'procurement/home_procurement.html')

def projects_list(request):
    projects = Project.objects.all()
    return render(request, 'procurement/projects_list.html', {'projects': projects})

def project_detail(request, project_id):
    project = get_object_or_404(Project, project_id=project_id)

    # Get the ProjectInventory instance linked to this project
    project_inventory = get_object_or_404(ProjectInventory, project=project)

    # Get all InventoryMaterial entries for the inventory
    materials_in_inventory = InventoryMaterial.objects.filter(inventory=project_inventory.inventory)

    context = {
        'project': project,
        'materials': [im.material for im in materials_in_inventory],  # list of Material objects
    }
    return render(request, 'procurement/project_detail.html', context)
