from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from .models import Product, Customer
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
import json
from .models import Customer, Product, Cart, Order

def product_list(request):
    products = Product.objects.all().values(
        "id", "name", "description", "price_cents", "quantity_in_stock"
    )
    return JsonResponse(list(products), safe=False)


def product_detail(request, pk):
    try:
        product = Product.objects.values(
            "id", "name", "description", "price_cents", "quantity_in_stock"
        ).get(pk=pk)
    except Product.DoesNotExist:
        raise Http404("Product not found")
    return JsonResponse(product)


@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 1))

    try:
        customer = Customer.objects.get(user=request.user)

        customer.cart.add_product(product=product, quantity=quantity)

        messages.success(request, f'Добавлено в корзину: {product.name} × {quantity}')

    except Customer.DoesNotExist:
        messages.error(request, 'Сначала зарегистрируйтесь!')

    except ValidationError as e:

        messages.error(request, str(e))

    return redirect('shop:product_list')


@csrf_exempt
@require_http_methods(["POST"])
def add_to_cart(request):
    """Добавляет товар в корзину пользователя"""
    try:
        data = json.loads(request.body)
        customer_id = data.get("customer_id")
        product_id = data.get("product_id")
        quantity = data.get("quantity", 1)

        customer = Customer.objects.get(id=customer_id)

        # Создаем корзину, если её нет
        cart, created = Cart.objects.get_or_create(customer=customer)

        product = Product.objects.get(id=product_id)

        # Используем бизнес-логику модели
        cart_item = cart.add_product(product, quantity)

        return JsonResponse({
            "success": True,
            "message": "Товар добавлен в корзину",
            "cart_item_id": cart_item.id,
            "quantity": cart_item.quantity
        })

    except Customer.DoesNotExist:
        return JsonResponse({"error": "Клиент не найден"}, status=404)
    except Product.DoesNotExist:
        return JsonResponse({"error": "Товар не найден"}, status=404)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": "Внутренняя ошибка сервера"}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def get_cart(request, customer_id):
    """Возвращает содержимое корзины"""
    try:
        customer = Customer.objects.get(id=customer_id)
        cart = customer.cart

        items_data = []
        total_price = 0

        for item in cart.items.all():
            item_data = {
                "product_id": item.product.id,
                "product_name": item.product.name,
                "price_cents": item.product.price_cents,
                "quantity": item.quantity,
                "total_cents": item.product.price_cents * item.quantity
            }
            items_data.append(item_data)
            total_price += item_data["total_cents"]

        return JsonResponse({
            "cart_id": cart.id,
            "items": items_data,
            "total_price_cents": total_price
        })

    except Customer.DoesNotExist:
        return JsonResponse({"error": "Клиент не найден"}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def create_order(request, customer_id):
    """Оформляет заказ из корзины"""
    try:
        customer = Customer.objects.get(id=customer_id)
        cart, created = Cart.objects.get_or_create(customer=customer)

        # Вызываем метод checkout()
        order = cart.checkout()

        return JsonResponse({
            "success": True,
            "message": "Заказ успешно оформлен",
            "order_id": order.id,
            "order_number": f"#{order.id}",
            "total_cents": order.total_cents,
            "status": order.get_status_display()
        })

    except Customer.DoesNotExist:
        return JsonResponse({"error": "Клиент не найден"}, status=404)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Ошибка при оформлении: {str(e)}"}, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def order_detail(request, customer_id, order_id):
    """Детали заказа"""
    try:
        customer = Customer.objects.get(id=customer_id)
        order = Order.objects.get(id=order_id, customer=customer)

        items_data = []
        for item in order.items.all():
            items_data.append({
                "product_name": item.product.name,
                "quantity": item.quantity,
                "price_cents": item.price_cents,
                "total_cents": item.price_cents * item.quantity
            })

        return JsonResponse({
            "order_id": order.id,
            "status": order.get_status_display(),
            "total_cents": order.total_cents,
            "created_at": order.created_at.isoformat(),
            "items": items_data
        })

    except (Customer.DoesNotExist, Order.DoesNotExist):
        return JsonResponse({"error": "Заказ не найден"}, status=404)


@csrf_exempt
@require_http_methods(["GET"])
def order_history(request, customer_id):
    """История заказов клиента"""
    try:
        customer = Customer.objects.get(id=customer_id)
        orders = Order.objects.filter(customer=customer).order_by('-created_at')

        orders_data = []
        for order in orders:
            orders_data.append({
                "id": order.id,
                "status": order.get_status_display(),
                "total_cents": order.total_cents,
                "created_at": order.created_at.isoformat(),
                "items_count": order.items.count()
            })

        return JsonResponse({"orders": orders_data})

    except Customer.DoesNotExist:
        return JsonResponse({"error": "Клиент не найден"}, status=404)

