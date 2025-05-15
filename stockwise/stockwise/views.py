from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import View
from user_management.models import Profile

class HomePageView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            user_profile = request.user.profile
            user_type = user_profile.user_type
        except Profile.DoesNotExist:
            return redirect('user_management:login')

        if user_type == 'manager':
            return redirect('project_management:home_manager')
        elif user_type == 'warehouse':
            return redirect('warehouse:home_warehouse')
        elif user_type == 'procurement':
            return redirect('procurement:home_procurement')
        elif user_type == 'supplier':
            return redirect('supply:home_supplier')
        else:
            # Fallback for unknown user types
            return redirect('user_management:login')