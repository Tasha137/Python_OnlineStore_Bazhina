from .models import Product, Cart


def add_to_cart(cart, product_id, quantity):
    """Простое добавление (без CartItem пока)"""
    product = Product.objects.get(id=product_id)

    if quantity > product.quantity_in_stock:
        raise ValueError(f"Недостаточно товара. Доступно: {product.quantity_in_stock}")

    # Сохраняем в product (упрощённо)
    product.quantity_in_stock -= quantity
    product.save()

    return {'status': 'added', 'quantity': quantity}

