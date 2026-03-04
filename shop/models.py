from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User


class Product(models.Model):
    name = models.CharField(max_length=200)
    price_cents = models.IntegerField()
    quantity_in_stock = models.IntegerField()


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    address = models.TextField()
