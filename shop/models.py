from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class Customer(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer")
    full_name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.full_name


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    description = models.TextField(blank=True)
    price_cents = models.PositiveBigIntegerField()
    quantity_in_stock = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"Cart #{self.id} for {self.customer.full_name}"

    @transaction.atomic
    def add_product(self, product, quantity=1):
        if quantity <= 0:
            raise ValidationError("Количество должно быть больше 0")
        if product.quantity_in_stock < quantity:
            raise ValidationError(f"На складе только {product.quantity_in_stock} шт.")

        cart_item, created = CartItem.objects.get_or_create(
            cart=self,
            product=product,
            defaults={"quantity": quantity}
        )
        if not created:
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.quantity_in_stock:
                raise ValidationError("Недостаточно товара на складе")
            cart_item.quantity = new_quantity
            cart_item.save()
        return cart_item

    def get_total_price(self):
        items = CartItem.objects.filter(cart=self)
        total = sum(item.product.price_cents * item.quantity for item in items)
        return total

    def clear(self):
        CartItem.objects.filter(cart=self).delete()

    def checkout(self):
        """Оформляет заказ из корзины"""
        # Проверяем, что корзина не пуста
        items = CartItem.objects.filter(cart=self)
        if not items.exists():
            raise ValidationError("Корзина пуста")

        # Проверяем остатки всех товаров
        for item in items:
            if item.quantity > item.product.quantity_in_stock:
                raise ValidationError(
                    f"Товара '{item.product.name}' недостаточно на складе "
                    f"(осталось {item.product.quantity_in_stock})"
                )

        # Создаем заказ
        total_price = self.get_total_price()
        order = Order.objects.create(
            customer=self.customer,
            total_cents=total_price
        )

        # Переносим товары в OrderItem и списываем со склада
        for cart_item in items:
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price_cents=cart_item.product.price_cents
            )

            # ПРОСТОЕ списание со склада БЕЗ F
            product = cart_item.product
            product.quantity_in_stock -= cart_item.quantity
            product.save()

        # Очищаем корзину
        self.clear()

        return order


class CartItem(models.Model):
    id = models.AutoField(primary_key=True)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="cart_items")
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    STATUS_CHOICES = [
        ("pending", "В обработке"),
        ("paid", "Оплачен"),
        ("shipped", "Отправлен"),
        ("delivered", "Доставлен"),
        ("cancelled", "Отменён"),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name="orders")
    total_cents = models.PositiveBigIntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.id}"

    def get_total_price(self):
        items = OrderItem.objects.filter(order=self)
        total = sum(item.price_cents * item.quantity for item in items)
        return total


class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="order_items")
    quantity = models.PositiveIntegerField()
    price_cents = models.PositiveBigIntegerField()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
