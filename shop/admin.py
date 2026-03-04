from django.contrib import admin
from .models import Product, Customer  # ← Убрал Cart, CartItem!

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_cents', 'quantity_in_stock']

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone']
