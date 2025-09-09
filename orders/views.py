from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
import stripe
from products.models import Product
from .models import Order, OrderItem
from decimal import Decimal

stripe.api_key = settings.STRIPE_SECRET_KEY

def add_to_cart(request, product_id):
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, id=product_id)
    if product.inventory > 0:
        cart[str(product_id)] = cart.get(str(product_id), 0) + 1
        request.session['cart'] = cart
        messages.success(request, f"{product.name} added to cart.")
    else:
        messages.error(request, f"{product.name} is out of stock.")
    return redirect('orders:cart')

def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product = get_object_or_404(Product, id=product_id)
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        messages.success(request, f"{product.name} removed from cart.")
    return redirect('orders:cart')

def view_cart(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())
    cart_items = [{'product': p, 'quantity': cart[str(p.id)], 'total': p.price * cart[str(p.id)]} for p in products]
    total_price = sum(item['total'] for item in cart_items)
    return render(request, 'orders/cart.html', {'cart_items': cart_items, 'total_price': total_price})

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Your cart is empty.")
        return redirect('orders:cart')
    products = Product.objects.filter(id__in=cart.keys())
    cart_items = [{'product': p, 'quantity': cart[str(p.id)], 'total': p.price * cart[str(p.id)]} for p in products]
    total_price = sum(p.price * cart[str(p.id)] for p in products)
    order = Order.objects.create(user=request.user, total_price=total_price)
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        OrderItem.objects.create(order=order, product=product, quantity=quantity, price=product.price)
        product.inventory -= quantity
        product.save()
    request.session['cart'] = {}
    tax_amount = order.tax_amount
    messages.success(request, "Order created successfully. Proceed to payment.")
    return render(request, 'orders/checkout.html', {
        'cart_items': cart_items,
        'total_price': total_price,
        'tax_amount': tax_amount,
        'order_id': order.id,
        'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY
    })

@login_required
def create_checkout_session(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': f'Order {order.id}'},
                'unit_amount': int((order.total_price + order.tax_amount) * 100),
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri('/orders/success/'),
        cancel_url=request.build_absolute_uri('/orders/cancel/'),
        client_reference_id=str(order.id),
    )
    order.stripe_payment_id = session.id
    order.save()
    return JsonResponse({'id': session.id})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return JsonResponse({'status': 'invalid payload'}, status=400)
    except stripe.error.SignatureVerificationError:
        return JsonResponse({'status': 'invalid signature'}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session['client_reference_id']
        order = Order.objects.get(id=order_id)
        order.status = 'PROCESSING'
        order.save()
    return JsonResponse({'status': 'success'})