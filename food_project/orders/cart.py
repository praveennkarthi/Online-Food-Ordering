from decimal import Decimal

from .models import MenuItem, Restaurant


class Cart:
    KEY = "cart"

    def __init__(self, request):
        self.session = request.session
        self.data = self.session.get(self.KEY) or {"restaurant_id": None, "items": {}}
        self._lines = None

    def _save(self):
        self.session[self.KEY] = self.data
        self.session.modified = True
        self._lines = None

    def add(self, item, qty=1):
        replaced = bool(self.data["items"]) and self.data["restaurant_id"] != item.restaurant_id
        if self.data["restaurant_id"] != item.restaurant_id:
            self.data = {"restaurant_id": item.restaurant_id, "items": {}}
        key = str(item.id)
        self.data["items"][key] = self.data["items"].get(key, 0) + qty
        self._save()
        return replaced

    def set_quantity(self, item_id, qty):
        key = str(item_id)
        if key in self.data["items"]:
            if qty <= 0:
                del self.data["items"][key]
            else:
                self.data["items"][key] = min(qty, 20)
            if not self.data["items"]:
                self.data["restaurant_id"] = None
            self._save()

    def remove(self, item_id):
        self.set_quantity(item_id, 0)

    def clear(self):
        self.data = {"restaurant_id": None, "items": {}}
        self._save()

    @property
    def lines(self):
        if self._lines is None:
            ids = [int(i) for i in self.data["items"]]
            found = MenuItem.objects.filter(id__in=ids, is_available=True)
            self._lines = [
                {"item": m, "quantity": self.data["items"][str(m.id)],
                 "subtotal": m.price * self.data["items"][str(m.id)]}
                for m in found
            ]
        return self._lines

    @property
    def total(self):
        return sum((l["subtotal"] for l in self.lines), Decimal("0"))

    @property
    def count(self):
        return sum(self.data["items"].values())

    @property
    def restaurant(self):
        rid = self.data["restaurant_id"]
        return Restaurant.objects.filter(pk=rid).first() if rid else None
