from decimal import Decimal
from django.test import TestCase
from main import models


class TestModel(TestCase):
    def test_active_manager_works(self):
        models.Product.objects.create(
            name="Adult Hat",
            price=Decimal("10.00"))
        models.Product.objects.create(
            name="Child Hat",
            price=Decimal("6.00"))
        models.Product.objects.create(
            name="Scarf",
            price=Decimal("12.00"),
            active=False)
        self.assertEqual(len(models.Product.objects.active()), 2)
