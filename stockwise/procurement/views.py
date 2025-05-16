from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from user_management.decorators import user_type_required
from stock_management.models import Project, ProjectInventory, InventoryMaterial, PurchaseRequest, RequestDetail, Material
from django.utils import timezone
from .forms import RequestMaterialForm

from django.forms import formset_factory
import uuid
import random
import string
from collections import defaultdict

@login_required
@user_type_required('procurement')
def home_procurement(request):
    return render(request, 'home_procurement.html')

@login_required
def projects_list(request):
    projects = Project.objects.all()
    return render(request, 'projects_list.html', {'projects': projects})

@login_required
def project_detail(request, project_id):
    project = get_object_or_404(Project, project_id=project_id)
    project_inventory = get_object_or_404(ProjectInventory, project=project)
    materials_in_inventory = InventoryMaterial.objects.filter(inventory=project_inventory.inventory).select_related('material')

    context = {
        'project': project,
        'materials_in_inventory': materials_in_inventory,
    }
    return render(request, 'project_detail.html', context)

def generate_pr_id():
    while True:
        pr_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if not PurchaseRequest.objects.filter(pr_id=pr_id).exists():
            return pr_id

@login_required
def request_material(request, project_id):
    project = get_object_or_404(Project, project_id=project_id)

    # Get all materials, grouped by material_type
    materials = Material.objects.all().order_by('material_type', 'material_name')
    grouped_materials = defaultdict(list)
    for m in materials:
        grouped_materials[m.material_type].append((m.material_id, m.material_name))

    # This will be the grouped choices format Django expects:
    grouped_choices = list(grouped_materials.items())  # [('Type1', [(id, name), ...]), ('Type2', [...])]

    # Create a formset for RequestMaterialForm
    MaterialFormSet = formset_factory(RequestMaterialForm, extra=0, min_num=1, validate_min=True)

    if request.method == "POST":
        formset = MaterialFormSet(request.POST)

        # Dynamically assign grouped choices to each form field for validation
        for form in formset:
            form.fields['material'].choices = grouped_choices

        if formset.is_valid():
            pr = PurchaseRequest.objects.create(
                pr_id=generate_pr_id(),
                request_date=timezone.now(),
                last_updated=timezone.now(),
                request_status='Waiting for Approval',
                project=project,
                requested_by=request.user,
            )

            for form in formset:
                detail = form.save(commit=False)
                detail.pr = pr
                detail.request_detail_id = str(uuid.uuid4()).replace('-', '')[:5]
                detail.save()

            return redirect('procurement:projects_list')
    else:
        formset = MaterialFormSet()
        # Assign grouped choices for initial GET request rendering
        for form in formset:
            form.fields['material'].choices = grouped_choices

    return render(request, 'request_material_form.html', {
        'formset': formset,
        'project': project,
        'grouped_choices': grouped_choices,  # Pass here for template use
    })
