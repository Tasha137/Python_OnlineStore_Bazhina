from django.test import TestCase
from shop.models import Product, Customer
from django.contrib.auth.models import User

class ProductTestCase(TestCase):
    def test_product_creation(self):
        """Создание товара со всеми обязательными полями"""
        product = Product.objects.create(
            name='iPhone 15 Pro',
            price_cents=80000,
            quantity_in_stock=5
        )
        self.assertEqual(product.name, 'iPhone 15 Pro')
        self.assertEqual(product.price_cents, 80000)
        self.assertEqual(product.quantity_in_stock, 5)

    def test_product_str(self):
        """Проверка метода __str__"""
        product = Product.objects.create(
            name='Test Product',
            price_cents=1000,
            quantity_in_stock=10
        )
        self.assertEqual(str(product), 'Test Product')

class CustomerTestCase(TestCase):
    def test_customer_creation(self):
        """Тест создания клиента"""
        user = User.objects.create_user(username='testuser', password='123456')
        customer = Customer.objects.create(
            user=user,
            full_name='Иванов Иван Иванович',
            phone='+79991234567',
            address='Москва, ул. Тестовая 1'
        )
        self.assertEqual(customer.full_name, 'Иванов Иван Иванович')
        self.assertEqual(customer.phone, '+79991234567')
        self.assertEqual(customer.user.username, 'testuser')
