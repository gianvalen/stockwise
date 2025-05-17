from collections import defaultdict
import random
import string
import uuid

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Case, When, BooleanField, Value, F
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from stock_management.models import (
    Project,
    ProjectInventory,
    InventoryMaterial,
    PurchaseRequest,
    RequestDetail,
    Material,
    Offer,
)

from user_management.decorators import user_type_required
from .forms import RequestMaterialForm
from django.forms import formset_factory


@login_required
@user_type_required('procurement')
def home_procurement(request):
    return render(request, 'home_procurement.html')

@login_required
@user_type_required('procurement', 'manager')
def projects_list(request):
    projects = Project.objects.all()
    return render(request, 'projects_list.html', {'projects': projects})

@login_required
@user_type_required('procurement', 'manager')
def project_detail(request, project_id):
    project = get_object_or_404(Project, project_id=project_id)
    project_inventory = get_object_or_404(ProjectInventory, project=project)
    
    materials_in_inventory = InventoryMaterial.objects.filter(
        inventory=project_inventory.inventory
    ).select_related('material').annotate(
        is_low_stock=Case(
            When(quantity__lte=F('material__low_stock_threshold'), then=Value(True)),
            default=Value(False),
            output_field=BooleanField()
        )
    )

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
@user_type_required('procurement', 'manager')
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
                if form.cleaned_data.get('material'):  # safer .get()
                    detail = form.save(commit=False)
                    detail.pr = pr
                    detail.material = form.cleaned_data['material']
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

@login_required
@user_type_required('procurement')
def pending_offers(request):
    status_filter = request.GET.get('status')
    project_filter = request.GET.get('project')

    # Handle Approve/Reject actions
    if request.method == 'POST':
        offer_id = request.POST.get('offer_id')
        action = request.POST.get('action')
        offer = get_object_or_404(Offer, offer_id=offer_id)

        if action == 'accept':
            offer.offer_status = 'Accepted'
            messages.success(request, f"Offer {offer_id} has been accepted.")
        elif action == 'reject':
            offer.offer_status = 'Rejected'
            messages.success(request, f"Offer {offer_id} has been rejected.")

        offer.save()

        # Preserve filters on redirect
        query_params = []
        if status_filter:
            query_params.append(f"status={status_filter}")
        if project_filter:
            query_params.append(f"project={project_filter}")
        query_string = f"?{'&'.join(query_params)}" if query_params else ""
        return redirect(f"{request.path}{query_string}")

    # Base queryset
    offers = Offer.objects.all()

    # Apply filters
    if status_filter:
        offers = offers.filter(offer_status=status_filter)
    if project_filter:
        offers = offers.filter(
            offerrequestdetail__request_detail__pr__project__project_id=project_filter
        )

    # Get all projects for the dropdown
    all_projects = Project.objects.all()

    context = {
        'offers': offers,
        'status_filter': status_filter,
        'project_filter': project_filter,
        'all_projects': all_projects,
    }
    return render(request, 'pending_offers_proc.html', context)

@login_required
@user_type_required('procurement')
def my_requests(request):
    status_filter = request.GET.get('status')
    project_id_filter = request.GET.get('project')

    # Base queryset
    user_requests = PurchaseRequest.objects.filter(requested_by=request.user).order_by('-request_date')

    # Apply filters
    if status_filter:
        user_requests = user_requests.filter(request_status=status_filter)

    if project_id_filter:
        user_requests = user_requests.filter(project__project_id=project_id_filter)

    # Extract unique projects
    user_projects = (
        Project.objects.filter(purchaserequest__requested_by=request.user)
        .distinct()
    )

    return render(request, 'my_requests.html', {
        'requests': user_requests,
        'project_names': user_projects,  # Send full Project objects
    })