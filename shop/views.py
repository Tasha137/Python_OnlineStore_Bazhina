from .models import Product, Cart, CartItem, Order, OrderItem
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from .models import Customer
from django.contrib.auth.models import User
from django.db import transaction
from decimal import Decimal


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


def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if not username or not password1 or not password2:
            messages.error(request, 'Заполните все поля.')
            return render(request, 'shop/register.html')

        if password1 != password2:
            messages.error(request, 'Пароли не совпадают.')
            return render(request, 'shop/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Пользователь с таким именем уже существует.')
            return render(request, 'shop/register.html')

        user = User.objects.create_user(username=username, password=password1)
        login(request, user)
        return redirect('index')

    return render(request, 'shop/register.html')


@login_required
def cart(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    total = sum(item.item_total for item in cart_items)

    return render(request, 'shop/cart.html', {
        'cart_items': cart_items,
        'total': total,
    })

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, _ = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={
            'quantity': 1,
            'price': product.price_cents,
        }
    )

    if not created:
        if cart_item.quantity >= product.quantity_in_stock:
            messages.error(request, "Товара больше нет в наличии.")
            return redirect('cart')
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, "Товар добавлен в корзину.")
    return redirect('cart')

@login_required
def cart_remove(request, item_id):
    cart = get_object_or_404(Cart, user=request.user)
    item = get_object_or_404(CartItem, id=item_id, cart=cart)
    item.delete()
    return redirect('cart')

@login_required
def create_order(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        messages.error(request, 'Корзина не найдена.')
        return redirect('cart')

    cart_items = cart.items.all()
    if not cart_items.exists():
        messages.info(request, 'Корзина пуста.')
        return redirect('cart')

    try:
        with transaction.atomic():
            total_amount = sum((item.item_total for item in cart_items), Decimal('0.00'))
            order = Order.objects.create(user=request.user, total_amount=total_amount)

            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.price,
                )

            cart_items.delete()

        messages.success(request, f'Заказ #{order.id} создан!')
        return redirect('cart')

    except Exception as e:
        print("CREATE_ORDER_ERROR:", repr(e))
        messages.error(request, 'Не удалось создать заказ.')
        return redirect('cart')
