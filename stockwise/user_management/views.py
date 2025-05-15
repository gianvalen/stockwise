from django.shortcuts import render
from django.contrib.auth import login
from .forms import UserRegistrationForm

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})