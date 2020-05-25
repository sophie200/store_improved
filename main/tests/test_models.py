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
    
    def test_create_order_works(self):
        p1 = models.Product.objects.create(
            name="Adult Hat",
            price=Decimal("10.00"),
        )
        p2 = models.Product.objects.create(
            name="Child Hat",
            price=Decimal("6.00"),
        )
        user1 = models.User.objects.create_user(
            "user1", "pw432joij"
        )
        billing = models.AddressUpdate.objects.create(
            user=user1, 
            name="John Kimball", 
            address1="127 Strudel road",
            city="London",
            country="uk",
        )
        shipping = models.AddressUpdate.objects.create(
            user=user1, 
            name="John Kimball", 
            address1="127 Deacon road",
            city="London",
            country="uk",
        )

        basket = models.Basket.objects.create(user=user1)
        models.BasketLine.objects.create(
            basket=basket, product=p1
        )
        models.BasketLine.objects.create(
            basket=basket, product=p2
        )

        with self.assertLogs("main.models", level="INFO") as cm:
            order = basket.create_order(billing, shipping)
        
        self.assertEqual(basket.cost_display(), 16.00)
        self.assertGreaterEqual(len(cm.output), 1)

        order.refresh_from_db()

        self.assertEquals(order.user, user1)
        self.assertEquals(
            order.billing_address1, billing.address1
        )
        self.assertEquals(
            order.shipping_address1, shipping.address1
        )

        self.assertEquals(order.lines.all().count(), 2)
        lines = order.lines.all()
        self.assertEquals(lines[0].product, p1)
        self.assertEquals(lines[1].product, p2)
