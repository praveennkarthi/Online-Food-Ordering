
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import CheckoutForm
from .models import (
    MenuItem,
    Order,
    OrderItem,
    Restaurant,
    Product,
)


# ---------- Restaurant & Product Search ----------



def restaurant_list(request):
    q = request.GET.get("q", "").strip()

    restaurants = Restaurant.objects.all()
    products = Product.objects.filter(is_available=True)

    if q:
        restaurants = restaurants.filter(
            Q(name__icontains=q)
            | Q(cuisine__icontains=q)
            | Q(items__name__icontains=q)
            | Q(products__name__icontains=q)
            | Q(products__category__icontains=q)
        ).distinct()

        products = products.filter(
            Q(name__icontains=q)
            | Q(category__icontains=q)
            | Q(restaurant__name__icontains=q)
        )

    return render(
        request,
        "restaurant_list.html",
        {
            "restaurants": restaurants,
            "products": products,
            "q": q,
        },
    )




# ---------- Restaurant Details ----------

def restaurant_detail(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)

    items = restaurant.items.filter(is_available=True)

    products = restaurant.products.filter(is_available=True)

    return render(
        request,
        "restaurant_detail.html",
        {
            "restaurant": restaurant,
            "items": items,
            "products": products,
        },
    )
# ---------- Cart ----------

@require_POST
def add_to_cart(request, item_id):
    item = get_object_or_404(
        MenuItem,
        pk=item_id,
        is_available=True
    )

    if not item.restaurant.is_open:
        messages.error(
            request,
            f"{item.restaurant.name} is closed right now."
        )

        return redirect(
            "restaurant_detail",
            pk=item.restaurant_id
        )

    if Cart(request).add(item):
        messages.info(
            request,
            "You can only order from one restaurant at a time, "
            "so your cart was cleared first."
        )

    messages.success(
        request,
        f"{item.name} added to your cart."
    )

    return redirect(
        "restaurant_detail",
        pk=item.restaurant_id
    )


def cart_view(request):
    return render(
        request,
        "cart.html",
        {
            "cart": Cart(request)
        }
    )


@require_POST
def update_cart(request, item_id):
    try:
        qty = int(
            request.POST.get("quantity", 1)
        )
    except ValueError:
        qty = 1

    Cart(request).set_quantity(
        item_id,
        qty
    )

    return redirect("cart")


@require_POST
def remove_from_cart(request, item_id):
    Cart(request).remove(item_id)

    return redirect("cart")


# ---------- Checkout & Orders ----------

@login_required
def checkout(request):
    cart = Cart(request)

    if not cart.lines:
        messages.warning(
            request,
            "Add something to your cart before checking out."
        )

        return redirect("restaurant_list")

    form = CheckoutForm(
        request.POST or None
    )

    if request.method == "POST" and form.is_valid():

        with transaction.atomic():

            order = Order.objects.create(
                user=request.user,
                restaurant=cart.restaurant,
                total=cart.total,
                address=form.cleaned_data["address"],
                phone=form.cleaned_data["phone"],
            )

            OrderItem.objects.bulk_create([
                OrderItem(
                    order=order,
                    menu_item=line["item"],
                    name=line["item"].name,
                    price=line["item"].price,
                    quantity=line["quantity"],
                )
                for line in cart.lines
            ])

        cart.clear()

        messages.success(
            request,
            f"Order #{order.pk} placed."
        )

        return redirect(
            "order_detail",
            pk=order.pk
        )

    return render(
        request,
        "checkout.html",
        {
            "cart": cart,
            "form": form,
        },
    )


# ---------- Order History ----------

@login_required
def order_list(request):
    orders = request.user.orders.select_related(
        "restaurant"
    )

    return render(
        request,
        "order_list.html",
        {
            "orders": orders
        },
    )


# ---------- Order Details & Tracking ----------

@login_required
def order_detail(request, pk):
    order = get_object_or_404(
        Order,
        pk=pk,
        user=request.user
    )

    return render(
        request,
        "order_detail.html",
        {
            "order": order,
            "steps": order.tracker(),
        },
    )


# ---------- Cancel Order ----------

@login_required
@require_POST
def cancel_order(request, pk):
    order = get_object_or_404(
        Order,
        pk=pk,
        user=request.user
    )

    if order.can_cancel:

        order.status = Order.Status.CANCELLED

        order.save(
            update_fields=[
                "status",
                "updated_at"
            ]
        )

        messages.success(
            request,
            "Order #%d cancelled." % order.pk
        )

    else:
        messages.error(
            request,
            "This order is already being prepared "
            "and can't be cancelled."
        )

    return redirect(
        "order_detail",
        pk=pk
    )


# ---------- User Registration ----------

def register(request):
    form = UserCreationForm(
        request.POST or None
    )

    if request.method == "POST" and form.is_valid():

        user = form.save()

        login(
            request,
            user
        )

        return redirect(
            "restaurant_list"
        )

    return render(
        request,
        "registration/register.html",
        {
            "form": form
        },
    )


# ---------- Add Product to Cart ----------

@require_POST
def add_product_to_cart(request, product_id):
    product = get_object_or_404(
        Product,
        pk=product_id,
        is_available=True
    )

    restaurant = product.restaurant

    if not restaurant.is_open:
        messages.error(request, f"{restaurant.name} is closed right now.")
        return redirect("restaurant_detail", pk=restaurant.pk)

    item, created = MenuItem.objects.get_or_create(
        restaurant=restaurant,
        name=product.name,
        defaults={
            "price": product.price,
            "description": product.description,
            "is_veg": product.is_veg,
            "is_available": True,
        },
    )

    if not created and (item.price != product.price or not item.is_available):
        item.price = product.price
        item.is_available = True
        item.save()

    if Cart(request).add(item):
        messages.info(
            request,
            "You can only order from one restaurant at a time, "
            "so your cart was cleared first."
        )

    messages.success(request, f"{product.name} added to your cart.")
    return redirect("restaurant_detail", pk=restaurant.pk)