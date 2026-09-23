from django.contrib.auth import login as auth_login
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render

from .forms import CustomUserCreationForm

CUSTOMER_GROUP_NAME = 'Customers'


def register(request):
    if request.user.is_authenticated:
        return redirect('core:home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            customer_group, _ = Group.objects.get_or_create(name=CUSTOMER_GROUP_NAME)
            user.groups.add(customer_group)
            auth_login(request, user)
            return redirect('core:home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})
