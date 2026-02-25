from django.urls import path
from . import views

urlpatterns = [
    path("products/", views.product_list, name="product_list"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("cart/add/", views.add_to_cart, name="add_to_cart"),
    path("cart/<int:customer_id>/", views.get_cart, name="get_cart"),
    path("orders/<int:customer_id>/", views.create_order, name="create_order"),
    path("orders/<int:customer_id>/<int:order_id>/", views.order_detail, name="order_detail"),
    path("orders/history/<int:customer_id>/", views.order_history, name="order_history"),
]
