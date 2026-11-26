# Namma Oota

A small food ordering site built with Django. Customers browse restaurants, fill a cart,
place an order and follow its status. Restaurant staff update orders from the Django admin.

## Running it locally

    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python manage.py migrate
    python manage.py seed_data
    python manage.py runserver

The site is at http://127.0.0.1:8000/. The admin is at /admin/ (user `admin`, password
`admin123`, created by `seed_data`; change it if you ever deploy this).

## How it works

- `orders/models.py` has Restaurant, MenuItem, Order and OrderItem.
- `orders/cart.py` keeps the cart in the session. A cart can only hold one restaurant's items.
- Orders move through Placed, Confirmed, Preparing, Out for Delivery and Delivered.
  Change the status in the admin and the customer's order page updates on its next refresh.
- Customers can cancel while an order is Placed or Confirmed.

## Tests

    python manage.py test
