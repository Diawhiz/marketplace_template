from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
import paystack
from products.models import Product
from .models import Order, OrderItem
from decimal import Decimal
import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import hmac
import hashlib
import logging

logger = logging.getLogger(__name__)

TAX_RATE = Decimal('0.005')

paystack.api_key = settings.PAYSTACK_SECRET_KEY

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
    try:
        cart = request.session.get('cart', {})
        if not cart:
            messages.error(request, "Your cart is empty.")
            logger.warning("Checkout attempted with empty cart.")
            return redirect('orders:cart')
        products = Product.objects.filter(id__in=cart.keys())
        if not products:
            messages.error(request, "No valid products in cart.")
            logger.warning("No valid products found in cart.")
            return redirect('orders:cart')
        cart_items = [{'product': p, 'quantity': cart[str(p.id)], 'total': p.price * cart[str(p.id)]} for p in products]
        total_price = sum(p.price * cart[str(p.id)] for p in products)
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            tax_amount=total_price * settings.TAX_RATE
        )
        order.save()  # Ensure the order is saved
        logger.info(f"Created order {order.id} for user {request.user.id}")
        for product_id, quantity in cart.items():
            product = Product.objects.get(id=product_id)
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=product.price)
            product.inventory -= quantity
            product.save()
        request.session['cart'] = {}
        messages.success(request, "Order created successfully. Proceed to payment.")
        return render(request, 'orders/checkout.html', {
            'cart_items': cart_items,
            'total_price': total_price,
            'tax_amount': order.tax_amount,
            'order_id': order.id,
            'order': order,
            'PAYSTACK_PUBLIC_KEY': settings.PAYSTACK_PUBLIC_KEY
        })
    except Exception as e:
        logger.error(f"Checkout failed: {str(e)}")
        messages.error(request, f"Checkout failed: {str(e)}")
        return redirect('orders:cart')

@login_required
def create_checkout_session(request, order_id):
    try:
        order = Order.objects.get(id=order_id, user=request.user)
        amount = int(order.total_price * 100)  # Paystack expects amount in kobo (NGN)
        from paystackapi.transaction import Transaction
        response = Transaction.initialize(
            reference=f'order_{order_id}_{request.user.id}',
            amount=amount,
            email=request.user.email,
            callback_url='http://127.0.0.1:8000/orders/success/'
        )
        if response['status']:
            return redirect(response['data']['authorization_url'])
        else:
            return redirect('orders:checkout')
    except Order.DoesNotExist:
        return redirect('orders:cart')
    except Exception as e:
        print(f"Error: {str(e)}")
        return redirect('orders:checkout')

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = [{
        'product': item.product,
        'quantity': item.quantity,
        'price': item.price,
        'total': item.price * item.quantity
    } for item in order.items.all()]
    return render(request, 'orders/order_detail.html', {
        'order': order,
        'items': items
    })

@csrf_exempt
@require_POST
def paystack_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_X_PAYSTACK_SIGNATURE')
    secret = settings.PAYSTACK_SECRET_KEY  # Use the secret key for verification

    # Verify webhook signature
    computed_hmac = hmac.new(
        key=secret.encode('utf-8'),
        msg=payload,
        digestmod=hashlib.sha512
    ).hexdigest()

    if sig_header != computed_hmac:
        return JsonResponse({'status': 'invalid signature'}, status=400)

    try:
        event = json.loads(payload)
        if event['event'] == 'charge.success':
            reference = event['data']['reference']
            from paystackapi.transaction import Transaction
            response = Transaction.verify(reference=reference)
            if response['status'] and response['data']['status'] == 'success':
                order_id = reference.split('_')[1]  # Extract order_id from reference
                order = Order.objects.get(id=order_id)
                order.status = 'PROCESSING'
                order.save()
                return JsonResponse({'status': 'success'})
    except Exception as e:
        print(f"Webhook error: {str(e)}")
        return JsonResponse({'status': 'invalid payload'}, status=400)

    return JsonResponse({'status': 'ignored'}, status=200)