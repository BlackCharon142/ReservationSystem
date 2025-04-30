from django.shortcuts import render
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required

class LoginViewPage(LoginView):
    template_name = 'login.htm'

def user_password_recovery(request):
    return render(request, template_name="user-password-recovery.htm")

@login_required
def dashboard(request):
    return render(request, template_name="dashboard.htm")

@login_required
def reserve(request):
    return render(request, template_name="reserve.htm")

@login_required
def reserved(request):
    return render(request, template_name="reserved.htm")