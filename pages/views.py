from django.shortcuts import render, redirect

from django.contrib.auth import login, authenticate
from pages.forms import LoginForm

from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required

from users.models import Profile


class LoginViewPage(LoginView):
    template_name = 'index.htm'
    form_class = LoginForm

@login_required
def logout(request):
    from django.contrib.auth import logout
    from django.shortcuts import redirect

    logout(request)
    return redirect('/')

def user_password_recovery(request):
    return render(request, template_name="user-password-recovery.htm")

@login_required
def dashboard(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, template_name="dashboard.htm", context={'profile': profile})

@login_required
def reserve(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, template_name="reserve.htm", context={'profile': profile})

@login_required
def reserved(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    return render(request, template_name="reserved.htm", context={'profile': profile})