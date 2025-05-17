from collections import defaultdict
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Case, When, BooleanField, Value, F
from django.utils import timezone
import uuid
import random
import string


from stock_management.models import (
    Inventory,
    InventoryMaterial,
    Material,
    Offer,
    OfferPurchaseOrder,
    Project,
    ProjectInventory,
    PurchaseOrder,
    PurchaseRequest,
    RequestDetail,
)

from user_management.decorators import user_type_required
from .forms import RequestMaterialForm
from django.forms import formset_factory

from .forms import MaterialTransferForm
from user_management.decorators import user_type_required
from django.contrib.auth.decorators import login_required

@login_required
@user_type_required('manager')
def home_manager(request):
    return render(request, 'project_management/home_manager.html')

@login_required
@user_type_required('manager')
def projects_list(request):
    projects = Project.objects.all()
    return render(request, 'project_management/projects_list.html', {'projects': projects})


@login_required
@user_type_required('manager')
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

    report = []
    for item in materials_in_inventory:
        if item.initial_quantity is None:
            item.initial_quantity = item.quantity
            item.save()

        total_used = max((item.initial_quantity - item.quantity) - item.transferred_out, 0)

        if item.initial_quantity > 0:
            percentage_used = (total_used / item.initial_quantity) * 100
        else:
            percentage_used = 0

        report.append({
            'material_name': item.material.material_name,
            'total_quantity': item.initial_quantity,
            'current_quantity': item.quantity,
            'total_used': total_used,
            'percentage_used': round(percentage_used, 2),
            'unit': item.material.unit,
            'transferred_quantity': item.transferred_out or 0,
        })

    context = {
        'project': project,
        'materials_in_inventory': materials_in_inventory,
        'report': report,
    }
    return render(request, 'project_management/project_detail.html', context)


def generate_pr_id():
    while True:
        pr_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if not PurchaseRequest.objects.filter(pr_id=pr_id).exists():
            return pr_id

@login_required
@user_type_required('manager')
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

            return redirect('project_management:projects_list')
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
@user_type_required('manager')
def pending_requests(request):
    status_filter = request.GET.get('status')
    project_filter = request.GET.get('project')

    if request.method == 'POST':
        pr_id = request.POST.get('pr_id')
        action = request.POST.get('action')

        purchase_request = get_object_or_404(PurchaseRequest, pr_id=pr_id)

        if action == 'approve':
            purchase_request.request_status = 'Approved'
        elif action == 'reject':
            purchase_request.request_status = 'Not Approved'

        purchase_request.save()

        query_params = []
        if status_filter:
            query_params.append(f'status={status_filter}')
        if project_filter:
            query_params.append(f'project={project_filter}')
        query_string = '&'.join(query_params)
        return redirect(f'{request.path}?{query_string}' if query_string else request.path)

    purchase_requests = PurchaseRequest.objects.all().prefetch_related('requestdetail_set', 'project')
    if status_filter:
        purchase_requests = purchase_requests.filter(request_status=status_filter)
    if project_filter:
        purchase_requests = purchase_requests.filter(project__project_id=project_filter)

    all_projects = Project.objects.all().order_by('project_name')

    context = {
        'purchase_requests': purchase_requests,
        'status_filter': status_filter,
        'project_filter': project_filter,
        'all_projects': all_projects,
    }
    return render(request, 'project_management/pending_requests.html', context)

def transfer_materials_home(request):
    projects = Project.objects.all()

    project_materials = []
    for project in projects:
        try:
            inventory = project.projectinventory.inventory
            materials = InventoryMaterial.objects.filter(inventory=inventory).select_related('material')
        except ProjectInventory.DoesNotExist:
            materials = []

        project_materials.append({
            'project': project,
            'materials': materials,
        })

    return render(request, 'project_management/transfer_materials_home.html', {
        'project_materials': project_materials,
    })

@login_required
@user_type_required('manager')
def transfer_material(request, project_id, material_id):
    source_project = get_object_or_404(Project, project_id=project_id)
    material = get_object_or_404(Material, material_id=material_id)
    source_inventory = source_project.projectinventory.inventory

    try:
        source_im = InventoryMaterial.objects.get(inventory=source_inventory, material=material)
    except InventoryMaterial.DoesNotExist:
        return redirect('project_management:transfer_materials')

    if request.method == 'POST':
        form = MaterialTransferForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            destination_project = form.cleaned_data['destination_project']
            destination_inventory = destination_project.projectinventory.inventory

            if source_im.quantity < quantity:
                form.add_error('quantity', "Not enough quantity in source inventory.")
            else:
                destination_im, created = InventoryMaterial.objects.get_or_create(
                    inventory=destination_inventory,
                    material=material,
                    defaults={'im_id': generate_new_im_id(), 'quantity': 0, 'transferred_out': 0}
                )

                try:
                    with transaction.atomic():
                        # Deduct quantity from source
                        source_im.quantity -= quantity
                        # Increment transferred_out on source
                        source_im.transferred_out += quantity
                        source_im.save()

                        # Add quantity to destination
                        destination_im.quantity += quantity
                        destination_im.save()

                    return redirect('project_management:transfer_materials')
                except Exception as e:
                    form.add_error(None, f"Transfer failed: {str(e)}")
    else:
        form = MaterialTransferForm()

    return render(request, 'project_management/transfer_material.html', {
        'form': form,
        'source_project': source_project,
        'material': material,
        'current_qty': source_im.quantity,
    })

def generate_new_im_id():
    last_im = InventoryMaterial.objects.order_by('-im_id').first()
    if last_im:
        last_id_num = int(last_im.im_id.strip('IM'))
        new_id_num = last_id_num + 1
    else:
        new_id_num = 1
    return f"IM{new_id_num:03d}"

@login_required
@user_type_required('manager')
def pending_offers_proj(request):
    status_filter = request.GET.get('status')
    project_filter = request.GET.get('project')

    if request.method == 'POST':
        offer_id = request.POST.get('offer_id')
        action = request.POST.get('action')

        offer = get_object_or_404(Offer, offer_id=offer_id)

        if action == 'approve':
            offer.offer_status_proj = 'Accepted'
            offer.save()

            # Create PurchaseOrder only if not already created for this offer
            existing_po = OfferPurchaseOrder.objects.filter(offer=offer).first()
            if not existing_po:
                po_id = generate_po_id()
                # Example: set delivery_date to 7 days from now
                delivery_date = timezone.now() + timezone.timedelta(days=7)

                po = PurchaseOrder.objects.create(
                    po_id=po_id,
                    delivery_date=delivery_date,
                    po_status='For Delivery',
                )

                OfferPurchaseOrder.objects.create(
                    po=po,
                    offer=offer,
                )

        elif action == 'reject':
            offer.offer_status_proj = 'Rejected'
            offer.save()

        query_params = []
        if status_filter:
            query_params.append(f'status={status_filter}')
        if project_filter:
            query_params.append(f'project={project_filter}')
        query_string = '&'.join(query_params)
        return redirect(f'{request.path}?{query_string}' if query_string else request.path)

    offers = Offer.objects.all().select_related('offerrequestdetail__request_detail__pr__project')

    if status_filter:
        offers = offers.filter(offer_status_proj=status_filter)
    if project_filter:
        offers = offers.filter(offerrequestdetail__request_detail__pr__project__project_id=project_filter)

    all_projects = Project.objects.all().order_by('project_name')

    context = {
        'offers': offers,
        'status_filter': status_filter,
        'project_filter': project_filter,
        'all_projects': all_projects,
    }

    return render(request, 'pending_offers_proj.html', context)

def generate_po_id():
    last_po = PurchaseOrder.objects.order_by('-po_id').first()
    if last_po:
        num = int(last_po.po_id[2:]) + 1
    else:
        num = 1
    return f"PO{num:03d}"  # Format: PO001, PO002, etc.
