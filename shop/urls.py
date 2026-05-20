# shop/urls.py
from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.home, name='home'),
    path('catalog/', views.catalog_page, name='catalog'),

    # НОВЫЕ ПУТИ ДЛЯ КОРЗИНЫ:
    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('cart/minus/<str:item_key>/', views.cart_minus, name='cart_minus'),
    path('cart/checkout/', views.checkout, name='checkout'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/products/', views.admin_products, name='admin_products'),
    path('dashboard/users/', views.admin_users, name='admin_users'),
    path('dashboard/orders/', views.admin_orders, name='admin_orders'),
path('dashboard/finances/', views.admin_finances, name='admin_finances'),
path('dashboard/team/', views.admin_team, name='admin_team'),
path('admin-panel/team/pay/<int:manager_id>/', views.pay_manager, name='pay_manager'),
]