from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from stock_management.models import PurchaseRequest, RequestDetail, ProjectInventory, InventoryMaterial, Project, Material
from .forms import MaterialTransferForm
from django.db import transaction

def home_manager(request):
    return render(request, 'project_management/home_manager.html')

def pending_requests(request):
    status_filter = request.GET.get('status')  # Get status filter from URL query

    if request.method == 'POST':
        pr_id = request.POST.get('pr_id')
        action = request.POST.get('action')  # 'approve' or 'reject'

        purchase_request = get_object_or_404(PurchaseRequest, pr_id=pr_id)

        if action == 'approve':
            purchase_request.request_status = 'Approved'
        elif action == 'reject':
            purchase_request.request_status = 'Not Approved'

        purchase_request.save()
        return redirect(f'{request.path}?status={status_filter or ""}')

    # Filter purchase requests by status if provided
    purchase_requests = PurchaseRequest.objects.all().prefetch_related('requestdetail_set')
    if status_filter:
        purchase_requests = purchase_requests.filter(request_status=status_filter)

    context = {
        'purchase_requests': purchase_requests,
        'status_filter': status_filter,
    }
    return render(request, 'project_management/pending_requests.html', context)

def transfer_materials_home(request):
    # Get all projects with their materials via InventoryMaterial
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


def transfer_material(request, project_id, material_id):
    source_project = get_object_or_404(Project, project_id=project_id)
    material = get_object_or_404(Material, material_id=material_id)
    source_inventory = source_project.projectinventory.inventory

    # Get source InventoryMaterial
    try:
        source_im = InventoryMaterial.objects.get(inventory=source_inventory, material=material)
    except InventoryMaterial.DoesNotExist:
        messages.error(request, "Material not linked to source inventory.")
        return redirect('project_management:transfer_materials')

    if request.method == 'POST':
        form = MaterialTransferForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            destination_project = form.cleaned_data['destination_project']
            destination_inventory = destination_project.projectinventory.inventory

            if source_im.quantity < quantity:
                messages.error(request, "Not enough quantity in source inventory.")
                return redirect('project_management:transfer_material_form', project_id=project_id, material_id=material_id)

            # Get or create destination InventoryMaterial
            destination_im, created = InventoryMaterial.objects.get_or_create(
                inventory=destination_inventory,
                material=material,
                defaults={'im_id': generate_new_im_id(), 'quantity': 0}
            )

            try:
                with transaction.atomic():
                    # Deduct from source
                    source_im.quantity -= quantity
                    source_im.save()

                    # Add to destination
                    destination_im.quantity += quantity
                    destination_im.save()

                messages.success(request, f"Transferred {quantity} {material.unit} of {material.material_name} from {source_project.project_name} to {destination_project.project_name}.")
                return redirect('project_management:transfer_materials')
            except Exception as e:
                messages.error(request, f"Transfer failed: {str(e)}")
    else:
        form = MaterialTransferForm()

    return render(request, 'project_management/transfer_material.html', {
        'form': form,
        'source_project': source_project,
        'material': material,
        'current_qty': source_im.quantity,
    })


def generate_new_im_id():
    # get all existing im_id's, assume they're like 'IM001', 'IM002' etc.
    last_im = InventoryMaterial.objects.order_by('-im_id').first()
    if last_im:
        last_id_num = int(last_im.im_id.strip('IM'))  # strip prefix
        new_id_num = last_id_num + 1
    else:
        new_id_num = 1
    return f"IM{new_id_num:03d}"  # e.g. IM001, IM002
