from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from user_management.decorators import user_type_required
from stock_management.models import Project, ProjectInventory, InventoryMaterial

from .forms import UpdateMaterialForm

@login_required
@user_type_required('warehouse')
def home_warehouse(request):
    return render(request, 'home_warehouse.html')

@login_required
def projects_list(request):
    projects = Project.objects.all()
    return render(request, 'warehouse/projects_list.html', {'projects': projects})

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, project_id=project_id)

    # Get the ProjectInventory instance linked to this project
    project_inventory = get_object_or_404(ProjectInventory, project=project)

    # Get all InventoryMaterial entries for the inventory
    materials_in_inventory = InventoryMaterial.objects.filter(inventory=project_inventory.inventory).select_related('material')

    context = {
        'project': project,
        'materials_in_inventory': materials_in_inventory,  # list of Material objects
    }
    return render(request, 'warehouse/project_detail.html', context)

@login_required
@user_type_required('warehouse')
def update_material_quantity(request, project_id, material_id):
    # Step 1: Get the project
    project = get_object_or_404(Project, project_id=project_id)

    # Step 2: Get the related inventory through ProjectInventory
    project_inventory = get_object_or_404(ProjectInventory, project=project)
    inventory = project_inventory.inventory

    # Step 3: Get the material and verify it's in that inventory
    inventory_material = get_object_or_404(InventoryMaterial, material__material_id=material_id, inventory=inventory)
    material = inventory_material.material

    # Step 4: Proceed with form handling
    if request.method == 'POST':
        form = UpdateMaterialForm(request.POST, instance=inventory_material)
        if form.is_valid():
            form.save()
            return redirect('warehouse:project_detail', project_id=project.project_id)
    else:
        form = UpdateMaterialForm(instance=inventory_material)

    return render(request, 'update_material.html', {
        'form': form,
        'material': material,
    })
