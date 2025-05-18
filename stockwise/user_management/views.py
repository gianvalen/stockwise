from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.forms import AuthenticationForm

from .models import Profile
from .forms import UserRegistrationForm

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)

            try:
                role = user.profile.user_type
            except Profile.DoesNotExist:
                messages.error(request, "Profile creation failed. Please contact support.")
                return redirect('user_management:register')

            if role == 'manager':
                return redirect('project_management:home_manager')
            elif role == 'warehouse':
                return redirect('warehouse:home_warehouse')
            elif role == 'procurement':
                return redirect('procurement:home_procurement')
            elif role == 'supplier':
                return redirect('supply:home_supplier')
            else:
                messages.warning(request, "Unknown role. Please contact admin.")
                return redirect('user_management:login')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            role = user.profile.user_type

            if role == 'manager':
                return redirect('project_management:home_manager')
            elif role == 'warehouse':
                return redirect('warehouse:home_warehouse')
            elif role == 'procurement':
                return redirect('procurement:home_procurement')
            elif role == 'supplier':
                return redirect('supply:home_supplier')

            return redirect('user_management:login')
    else:
        form = AuthenticationForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    auth_logout(request)
    return redirect('user_management:login')