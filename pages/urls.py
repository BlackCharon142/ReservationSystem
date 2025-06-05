from django.urls import path
from . import views
from .views import LoginViewPage

urlpatterns = [
    path('', LoginViewPage.as_view(), name='login'),
    path('logout/', views.logout, name='logout'),
    path("user-password-recovery/", views.user_password_recovery, name="user-password-recovery"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("reserve/", views.reserve, name="reserve"),
    path("reserved/", views.reserved, name="reserved"),
    path('ajax/get-meals/', views.get_meals_by_timestamp, name='get_meals_by_timestamp'),
    path('ajax/reserve/',   views.ajax_reserve,   name='ajax_reserve'),
    path('ajax/cancel/',    views.ajax_cancel,    name='ajax_cancel'),
    path('ajax/wallet-balance/', views.ajax_wallet_balance, name='ajax_wallet_balance'),
]