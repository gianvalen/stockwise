from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from stock_management.models import (
    InventoryMaterial,
    OfferPurchaseOrder,
    Project,
    ProjectInventory,
    PurchaseOrder,
)

from user_management.decorators import user_type_required

from .forms import UpdateMaterialForm


@login_required
@user_type_required('warehouse')
def home_warehouse(request):
    return render(request, 'home_warehouse.html')

@login_required
@user_type_required('warehouse')
def projects_list(request):
    projects = Project.objects.all()
    return render(request, 'warehouse/projects_list.html', {'projects': projects})

@login_required
@user_type_required('warehouse')
def project_detail(request, project_id):
    project = get_object_or_404(Project, project_id=project_id)

    # Get the ProjectInventory instance linked to this project
    project_inventory = get_object_or_404(ProjectInventory, project=project)

    # Get all InventoryMaterial entries for the inventory
    materials_in_inventory = InventoryMaterial.objects.filter(inventory=project_inventory.inventory).select_related('material')

    # Build the report
    report = []
    for item in materials_in_inventory:
        if item.initial_quantity is None:
            item.initial_quantity = item.quantity
            item.save()

        total_used = item.initial_quantity - item.quantity

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
        })

    context = {
        'project': project,
        'materials_in_inventory': materials_in_inventory,
        'report': report,
    }
    return render(request, 'warehouse/project_detail.html', context)

@login_required
@user_type_required('warehouse')
def update_material_quantity(request, project_id, material_id):
    project = get_object_or_404(Project, project_id=project_id)
    project_inventory = get_object_or_404(ProjectInventory, project=project)
    inventory = project_inventory.inventory
    inventory_material = get_object_or_404(InventoryMaterial, material__material_id=material_id, inventory=inventory)

    if request.method == 'POST':
        form = UpdateMaterialForm(request.POST, instance=inventory_material)
        if form.is_valid():
            updated_material = form.save(commit=False)

            # Save initial quantity only once
            if updated_material.initial_quantity is None:
                updated_material.initial_quantity = inventory_material.quantity

            updated_material.save()
            return redirect('warehouse:project_detail', project_id=project.project_id)
    else:
        form = UpdateMaterialForm(instance=inventory_material)

    return render(request, 'warehouse/update_material.html', {
        'form': form,
        'project': project,
        'material': inventory_material.material,
    })

@login_required
@user_type_required('warehouse')
def purchase_orders_list(request):
    status_filter = request.GET.get('status')
    project_filter = request.GET.get('project')

    if request.method == 'POST':
        po_id = request.POST.get('po_id')
        try:
            with transaction.atomic():
                po = PurchaseOrder.objects.select_for_update().get(po_id=po_id)

                if po.po_status == 'Completed':
                    messages.info(request, "This order is already completed.")
                else:
                    po.po_status = 'Completed'
                    po.save()

                    opo = OfferPurchaseOrder.objects.select_related(
                        'offer',
                        'offer__offerrequestdetail',
                        'offer__offerrequestdetail__request_detail',
                        'offer__offerrequestdetail__request_detail__material',
                        'offer__offerrequestdetail__request_detail__pr',
                        'offer__offerrequestdetail__request_detail__pr__project'
                    ).get(po=po)

                    offer = opo.offer
                    material = offer.offerrequestdetail.request_detail.material

                    # Get the project from the purchase order path
                    project = offer.offerrequestdetail.request_detail.pr.project

                    try:
                        project_inventory = ProjectInventory.objects.get(project=project)
                    except ProjectInventory.DoesNotExist:
                        messages.error(request, f"No inventory found for project {project.project_name}.")
                        return redirect('warehouse:purchase_orders_list')

                    inventory = project_inventory.inventory

                    inventory_material, created = InventoryMaterial.objects.get_or_create(
                        inventory=inventory,
                        material=material,
                        defaults={'im_id': generate_new_im_id(), 'quantity': 0, 'initial_quantity': 0}
                    )

                    inventory_material.quantity += offer.total_quantity
                    inventory_material.save()

                    messages.success(request, f"Purchase Order {po.po_id} completed and inventory updated.")

        except PurchaseOrder.DoesNotExist:
            messages.error(request, "Purchase order not found.")
        except OfferPurchaseOrder.DoesNotExist:
            messages.error(request, "OfferPurchaseOrder not found for this PO.")

        return redirect(request.get_full_path())

    purchase_orders = PurchaseOrder.objects.all().order_by('delivery_date').select_related(
        'offerpurchaseorder__offer__offerrequestdetail__request_detail__pr__project'
    )

    if status_filter:
        purchase_orders = purchase_orders.filter(po_status=status_filter)
    if project_filter:
        purchase_orders = purchase_orders.filter(
            offerpurchaseorder__offer__offerrequestdetail__request_detail__pr__project__project_id=project_filter
        )

    all_projects = Project.objects.all().order_by('project_name')

    return render(request, 'purchase_orders_list.html', {
        'purchase_orders': purchase_orders,
        'status_filter': status_filter,
        'project_filter': project_filter,
        'all_projects': all_projects,
    })

from django.db.models import Max

def generate_new_im_id():
    last_id = InventoryMaterial.objects.aggregate(max_id=Max('im_id'))['max_id']
    
    if last_id and last_id.startswith('IM'):
        try:
            last_num = int(last_id.strip('IM'))
        except ValueError:
            last_num = 0
    else:
        last_num = 0

    return f"IM{last_num + 1:03d}"