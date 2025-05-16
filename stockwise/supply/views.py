import random
import string
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from user_management.decorators import user_type_required
from stock_management.models import PurchaseRequest, RequestDetail, OfferRequestDetail, Offer, PurchaseOrder
from .forms import OfferForm

@login_required
@user_type_required('supplier')
def home_supplier(request):
    return render(request, 'home_supplier.html')
    # Fetch all purchase requests with their details

def requests_list(request):
    purchase_requests = PurchaseRequest.objects.select_related('project').filter(request_status='Approved')

    context = {
        'purchase_requests': purchase_requests
    }
    return render(request, 'requests_list.html', context)

@login_required
@user_type_required('supplier')
def requests_detail(request, pr_id):
    purchase_request = get_object_or_404(PurchaseRequest, pr_id=pr_id)
    request_details = RequestDetail.objects.select_related('material').filter(pr=purchase_request)

    context = {
        'purchase_request': purchase_request,
        'request_details': request_details
    }
    return render(request, 'requests_detail.html', context)

@login_required
@user_type_required('supplier')
def offer_material(request, pr_id, material_id):
    purchase_request = get_object_or_404(PurchaseRequest, pr_id=pr_id)
    request_detail = get_object_or_404(RequestDetail, pr=purchase_request, material__material_id=material_id)

    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.offer_id = generate_offer_id()
            offer.offer_date = timezone.now()
            offer.offer_status = "Pending"
            offer.offered_by = request.user
            offer.save()

            OfferRequestDetail.objects.create(
                offer=offer,
                request_detail=request_detail
            )

            return redirect('supply:requests_detail', pr_id=pr_id)
    else:
        form = OfferForm()

    context = {
        'form': form,
        'material': request_detail.material,
        'purchase_request': purchase_request,
        'requested_quantity': request_detail.quantity,
    }

    return render(request, 'offer_material.html', context)


def generate_offer_id():
    while True:
        offer_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        if not Offer.objects.filter(offer_id=offer_id).exists():
            return offer_id
        
@login_required
@user_type_required('supplier')
def my_offers(request):
    offers = Offer.objects.filter(offered_by=request.user).order_by('-offer_date')

    # Get filter params from GET
    status_filter = request.GET.get('status', '')
    project_filter = request.GET.get('project', '')

    if status_filter:
        offers = offers.filter(offer_status=status_filter)
    
    if project_filter:
        offers = offers.filter(
            offerrequestdetail__request_detail__pr__project__project_id=project_filter
        )

    # To show project filter dropdown options
    all_projects = (
        Offer.objects.filter(offered_by=request.user)
        .values_list('offerrequestdetail__request_detail__pr__project__project_id',
                     'offerrequestdetail__request_detail__pr__project__project_name')
        .distinct()
    )

    context = {
        'offers': offers,
        'status_filter': status_filter,
        'project_filter': project_filter,
        'all_projects': all_projects,
    }
    return render(request, 'my_offers.html', context)

@login_required
@user_type_required('supplier')
def purchase_order_tracker(request):
    user = request.user

    purchase_orders = PurchaseOrder.objects.filter(
        offerpurchaseorder__offer__offered_by=user
    ).order_by('-delivery_date')

    # Get filter params from GET
    status_filter = request.GET.get('status', '')
    project_filter = request.GET.get('project', '')

    if status_filter:
        purchase_orders = purchase_orders.filter(po_status=status_filter)

    if project_filter:
        purchase_orders = purchase_orders.filter(
            offerpurchaseorder__offer__offerrequestdetail__request_detail__pr__project__project_id=project_filter
        )

    # Fetch distinct projects from current user's purchase orders for dropdown
    all_projects = (
        PurchaseOrder.objects.filter(
            offerpurchaseorder__offer__offered_by=user
        )
        .values_list(
            'offerpurchaseorder__offer__offerrequestdetail__request_detail__pr__project__project_id',
            'offerpurchaseorder__offer__offerrequestdetail__request_detail__pr__project__project_name'
        )
        .distinct()
    )

    context = {
        'purchase_orders': purchase_orders,
        'status_filter': status_filter,
        'project_filter': project_filter,
        'all_projects': all_projects,
    }
    return render(request, 'purchase_order_tracker.html', context)