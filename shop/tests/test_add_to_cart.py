from decimal import Decimal

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from shop.models import Product, Cart, CartItem

User = get_user_model()


class AddToCartTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.product = Product.objects.create(
            name='Тестовый товар',
            price_cents=Decimal('100.00'),
            stock=2
        )
        self.client.login(username='testuser', password='testpass123')

    def test_add_to_cart_creates_item(self):
        url = reverse('add_to_cart', args=[self.product.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

        cart = Cart.objects.get(user=self.user)
        item = CartItem.objects.get(cart=cart, product=self.product)

        self.assertEqual(item.quantity, 1)
        self.assertEqual(item.price, self.product.price_cents)

    def test_add_to_cart_increases_quantity(self):
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=1,
            price=self.product.price_cents
        )

        url = reverse('add_to_cart', args=[self.product.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

        item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(item.quantity, 2)

    def test_cannot_add_more_than_stock(self):
        cart = Cart.objects.create(user=self.user)
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2,
            price=self.product.price_cents
        )

        url = reverse('add_to_cart', args=[self.product.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

        item = CartItem.objects.get(cart=cart, product=self.product)
        self.assertEqual(item.quantity, 2)
