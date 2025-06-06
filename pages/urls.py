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
    
    # ADMIN URLs
    path('admin/', views.admin_dashboard, name='admin'),
    
    path('admin/dashboard', views.admin_dashboard, name='admin_dashboard'),
    
    path('admin/users/', views.admin_users, name='admin_users'),
    path('admin/users/delete/<int:id>/', views.delete_user, name='delete_users'),
    
    path('admin/password-recovery-requests/', views.admin_password_recovery_requests, name='admin_password_recovery_requests'),
    
    path('admin/foods/', views.admin_foods, name='admin_foods'),
    path('admin/foods/delete/<int:id>/', views.delete_food, name='delete_food'),
    
    path('admin/drinks', views.admin_drinks, name='admin_drinks'),
    path('admin/drinks/delete/<int:id>/', views.delete_drink, name='delete_drink'),
    
    path('admin/sidedishes', views.admin_sidedishes, name='admin_sidedishes'),
    path('admin/sidedishes/delete/<int:id>/', views.delete_sidedish, name='delete_sidedish'),
    
    path('admin/daily-menu-items', views.admin_daily_menu_items, name='admin_daily_menu_items'),
    path('admin/daily-menu-items/delete/<int:id>/', views.delete_daily_menu_item, name='delete_daily_menu_item'),
    
    path('admin/reservations', views.admin_reservations, name='admin_reservations'),
    
    path('admin/guests', views.admin_guests, name='admin_guests'),
    path('admin/guests/delete/<int:id>/', views.delete_guest, name='delete_guests'),
    path('admin/guests/cancel-reservation/', views.cancel_reservation, name='cancel_guest_reservation'),
]