from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from stock_management.models import PurchaseRequest, RequestDetail, ProjectInventory, InventoryMaterial, Project, Material, Offer
from .forms import MaterialTransferForm
from django.db import transaction

def home_manager(request):
    return render(request, 'project_management/home_manager.html')

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

def transfer_material(request, project_id, material_id):
    source_project = get_object_or_404(Project, project_id=project_id)
    material = get_object_or_404(Material, material_id=material_id)
    source_inventory = source_project.projectinventory.inventory

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

            destination_im, created = InventoryMaterial.objects.get_or_create(
                inventory=destination_inventory,
                material=material,
                defaults={'im_id': generate_new_im_id(), 'quantity': 0}
            )

            try:
                with transaction.atomic():
                    source_im.quantity -= quantity
                    source_im.save()

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
    last_im = InventoryMaterial.objects.order_by('-im_id').first()
    if last_im:
        last_id_num = int(last_im.im_id.strip('IM'))
        new_id_num = last_id_num + 1
    else:
        new_id_num = 1
    return f"IM{new_id_num:03d}"

def pending_offers_proj(request):
    status_filter = request.GET.get('status')
    project_filter = request.GET.get('project')

    if request.method == 'POST':
        offer_id = request.POST.get('offer_id')
        action = request.POST.get('action')

        offer = get_object_or_404(Offer, offer_id=offer_id)

        if action == 'approve':
            offer.offer_status_proj = 'Accepted'
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