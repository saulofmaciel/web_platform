from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import UserCreationFormWithEmail
from rolepermissions.decorators import has_role_decorator

# Create your views here.
@has_role_decorator('site_admin')
def signup(request):
    template = 'accounts/signup.html'

    if request.method == 'POST':
        form = UserCreationFormWithEmail(request.POST)
        if form.is_valid():
            form.save()
            if request.user.is_authenticated:
                return redirect('certificate')
            else:
                return redirect('login')
    else:
        form = UserCreationFormWithEmail()

    context = {'form': form}
    return render(request, template, context)

@login_required
def user_list_view(request):
    template = 'accounts/user-list.html'
    data = User.objects.all()
    context = {'data': data }
    return render(request, template, context)

