from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from user_management.decorators import user_type_required
from stock_management.models import Project, ProjectInventory, InventoryMaterial, PurchaseRequest
from django.utils import timezone
from .forms import RequestMaterialForm 

import uuid

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

    # Get the ProjectInventory instance linked to this project
    project_inventory = get_object_or_404(ProjectInventory, project=project)

    # Get all InventoryMaterial entries for the inventory
    materials_in_inventory = InventoryMaterial.objects.filter(inventory=project_inventory.inventory)

    context = {
        'project': project,
        'materials': [im.material for im in materials_in_inventory],  # list of Material objects
    }
    return render(request, 'project_detail.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from stock_management.models import Project, PurchaseRequest, RequestDetail
from .forms import RequestMaterialForm

def request_material(request, project_id):
    project = get_object_or_404(Project, project_id=project_id)

    if request.method == "POST":
        form = RequestMaterialForm(request.POST)
        if form.is_valid():
            # Create PurchaseRequest instance
            purchase_request = PurchaseRequest(
                pr_id=str(uuid.uuid4()).replace('-', '')[:5],  # Generate 5-char ID here
                request_date=timezone.now(),
                last_updated=timezone.now(),
                request_status='Waiting for Approval',
                project=project,
                requested_by=request.user,
            )
            purchase_request.save()

            # Create RequestDetail instance but don't save yet
            request_detail = form.save(commit=False)
            request_detail.pr = purchase_request
            request_detail.request_detail_id = str(uuid.uuid4()).replace('-', '')[:5]  # Generate 5-char ID here
            request_detail.save()

            return redirect('procurement:projects_list')
    else:
        form = RequestMaterialForm()

    return render(request, 'request_material_form.html', {'form': form, 'project': project})

import random
import string

def generate_pr_id():
    while True:
        pr_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if not PurchaseRequest.objects.filter(pr_id=pr_id).exists():
            return pr_id
