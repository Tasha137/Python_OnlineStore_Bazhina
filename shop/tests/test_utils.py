from django.test import TestCase
from shop.models import Product


class BusinessLogicTest(TestCase):
    def test_stock_management(self):
        """Изолированная бизнес-логика: управление остатками"""
        product = Product.objects.create(
            name='iPhone 15 Pro',
            price_cents=80000,
            quantity_in_stock=10
        )

        # Бизнес-логика: покупка 3 штук
        initial_stock = product.quantity_in_stock
        product.quantity_in_stock -= 3
        product.save()
        product.refresh_from_db()

        self.assertEqual(product.quantity_in_stock, initial_stock - 3)
