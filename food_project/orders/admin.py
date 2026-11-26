from django.contrib import admin

from .models import MenuItem, Order, OrderItem, Restaurant, Product

class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ("name", "cuisine", "delivery_time", "is_open")
    list_editable = ("is_open",)
    search_fields = ("name", "cuisine")
    inlines = [MenuItemInline]


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "restaurant", "price", "is_veg", "is_available")
    list_filter = ("restaurant", "is_veg", "is_available")
    list_editable = ("price", "is_available")
    search_fields = ("name",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("name", "price", "quantity", "menu_item")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "restaurant", "total", "status", "created_at")
    list_editable = ("status",)        
    list_filter = ("status", "restaurant")
    readonly_fields = ("user", "restaurant", "total", "created_at")
    inlines = [OrderItemInline]
    actions = ["mark_confirmed", "mark_preparing", "mark_out_for_delivery", "mark_delivered"]

    @admin.action(description="Mark selected as Confirmed")
    def mark_confirmed(self, request, qs):
        qs.update(status=Order.Status.CONFIRMED)

    @admin.action(description="Mark selected as Preparing")
    def mark_preparing(self, request, qs):
        qs.update(status=Order.Status.PREPARING)

    @admin.action(description="Mark selected as Out for Delivery")
    def mark_out_for_delivery(self, request, qs):
        qs.update(status=Order.Status.OUT_FOR_DELIVERY)

    @admin.action(description="Mark selected as Delivered")
    def mark_delivered(self, request, qs):
        qs.update(status=Order.Status.DELIVERED)
    
     
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "restaurant",
        "category",
        "price",
        "is_veg",
        "is_available",
    )

    list_filter = (
        "restaurant",
        "category",
        "is_veg",
        "is_available",
    )

    list_editable = ("price", "is_available")

    search_fields = ("name", "category", "restaurant__name")
