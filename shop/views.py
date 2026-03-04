# shop/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Product, Customer


def index(request):
    """Главная страница - список всех товаров"""
    products = Product.objects.all()
    context = {
        'products': products,
        'title': 'Магазин'
    }
    return render(request, 'shop/index.html', context)


def product_list(request):
    """Список всех товаров"""
    products = Product.objects.all()
    return render(request, 'shop/product_list.html', {'products': products})


def product_detail(request, pk):
    """Детали конкретного товара"""
    product = Product.objects.get(pk=pk)
    return render(request, 'shop/product_detail.html', {'product': product})


@login_required
def profile(request):
    """Профиль пользователя"""
    customer = Customer.objects.filter(user=request.user).first()
    products = Product.objects.all()

    context = {
        'customer': customer,
        'products': products
    }
    return render(request, 'shop/profile.html', context)


def catalog(request):
    """Каталог товаров"""
    products = Product.objects.filter(quantity_in_stock__gt=0)
    return render(request, 'shop/catalog.html', {'products': products})
