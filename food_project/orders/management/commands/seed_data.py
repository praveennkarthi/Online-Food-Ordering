from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from orders.models import MenuItem, Restaurant

RESTAURANTS = [
    {
        "name": "Spice Garden", "cuisine": "North Indian", "delivery_time": 35,
        "address": "MG Road, Bengaluru",
        "description": "Tandoor and curry house. Everything is made to order, so rotis arrive hot.",
        "items": [
            ("Paneer Butter Masala", "Cottage cheese in a creamy tomato gravy", 240, True),
            ("Dal Tadka", "Yellow lentils tempered with garlic and cumin", 180, True),
            ("Butter Naan", "", 40, True),
            ("Chicken Biryani", "Basmati rice, bone-in chicken, raita on the side", 280, False),
            ("Butter Chicken", "Tandoori chicken in a mild makhani sauce", 310, False),
        ],
    },
    {
        "name": "Pizza Corner", "cuisine": "Italian", "delivery_time": 25,
        "address": "Indiranagar, Bengaluru",
        "description": "Thin-crust pizzas baked in a wood oven.",
        "items": [
            ("Margherita", "Tomato, mozzarella, basil", 220, True),
            ("Farmhouse", "Capsicum, onion, mushroom, sweet corn", 320, True),
            ("Pepperoni", "", 380, False),
            ("Garlic Bread", "Four pieces with cheese", 120, True),
        ],
    },
    {
        "name": "Dosa House", "cuisine": "South Indian", "delivery_time": 20,
        "address": "Jayanagar 4th Block, Bengaluru",
        "description": "Udupi-style tiffin, served with sambar and two chutneys.",
        "items": [
            ("Masala Dosa", "", 90, True),
            ("Idli Vada", "Two idlis, one vada", 70, True),
            ("Rava Kesari Bath", "Khara bath and kesari bath on one plate", 85, True),
            ("Filter Coffee", "", 40, True),
            ("Chicken Chettinad", "Spicy, pepper-heavy, goes well with parotta", 260, False),
        ],
    },
]


class Command(BaseCommand):
    help = "Load sample restaurants and menus, and create an admin user if none exists"

    def handle(self, *args, **options):
        for entry in RESTAURANTS:
            items = entry["items"]
            data = {k: v for k, v in entry.items() if k != "items"}
            restaurant, _ = Restaurant.objects.get_or_create(name=data["name"], defaults=data)
            for name, desc, price, veg in items:
                MenuItem.objects.get_or_create(
                    restaurant=restaurant, name=name,
                    defaults={"description": desc, "price": price, "is_veg": veg},
                )
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin123")
            self.stdout.write("Created admin user (admin / admin123)")
        self.stdout.write("Sample data loaded")
