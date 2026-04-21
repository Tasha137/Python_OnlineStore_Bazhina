from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:pk>/', views.product_detail, name='product_detail'),
    path('profile/', views.profile, name='profile'),
    path('catalog/', views.catalog, name='catalog'),
    path('register/', views.register, name='register'),
    path('cart/', views.cart, name='cart'),
    path('order/create/', views.create_order, name='create_order'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.cart_remove, name='cart_remove'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
]
