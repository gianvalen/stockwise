from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from user_management.decorators import user_type_required
from stock_management.models import PurchaseRequest, RequestDetail, Project

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
