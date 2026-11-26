from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import MenuItem, Order


class OrderFlowTests(TestCase):
    def setUp(self):
        call_command("seed_data", verbosity=0)
        self.user = get_user_model().objects.create_user("bob", password="pass12345")

    def test_full_flow(self):
        item = MenuItem.objects.get(name="Masala Dosa")
        self.client.post(reverse("add_to_cart", args=[item.id]))
        self.client.post(reverse("add_to_cart", args=[item.id]))
        self.assertContains(self.client.get(reverse("cart")), "180")

        # checkout needs login
        self.assertEqual(self.client.get(reverse("checkout")).status_code, 302)
        self.client.login(username="bob", password="pass12345")
        resp = self.client.post(reverse("checkout"), {"address": "12 MG Road", "phone": "9876543210"})
        order = Order.objects.get()
        self.assertRedirects(resp, reverse("order_detail", args=[order.id]))
        self.assertEqual(order.total, 180)
        self.assertEqual(order.items.first().quantity, 2)

        # cancel works while PLACED
        self.client.post(reverse("cancel_order", args=[order.id]))
        order.refresh_from_db()
        self.assertEqual(order.status, "CANCELLED")

    def test_cart_resets_for_other_restaurant(self):
        a = MenuItem.objects.get(name="Masala Dosa")
        b = MenuItem.objects.get(name="Margherita")
        self.client.post(reverse("add_to_cart", args=[a.id]))
        self.client.post(reverse("add_to_cart", args=[b.id]))
        self.assertEqual(self.client.session["cart"]["restaurant_id"], b.restaurant_id)
        self.assertEqual(len(self.client.session["cart"]["items"]), 1)

    def test_cannot_view_others_orders(self):
        other = get_user_model().objects.create_user("eve", password="pass12345")
        order = Order.objects.create(user=other, restaurant_id=1, total=10, address="x", phone="1234567890")
        self.client.login(username="bob", password="pass12345")
        self.assertEqual(self.client.get(reverse("order_detail", args=[order.id])).status_code, 404)
