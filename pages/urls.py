from django.urls import path
from . import views
from .views import LoginViewPage

urlpatterns = [
    path('login/', LoginViewPage.as_view(), name='login'),
    path("user-password-recovery/", views.user_password_recovery, name="user-password-recovery"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("reserve/", views.reserve, name="reserve"),
    path("reserved/", views.reserved, name="reserved"),
]