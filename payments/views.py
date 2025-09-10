import paystack
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Order, Payment
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from orders.models import Order
from decimal import Decimal

paystack.api_key = settings.PAYSTACK_SECRET_KEY

# TAX_RATE = Decimal('0.05')

@login_required
def create_checkout_session(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    session = paystack.checkout.Session.create(
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
    order.paystack_payment_id = session.id
    order.save()
    return JsonResponse({'id': session.id})


@csrf_exempt
def paystack_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_PAYSTACK_SIGNATURE')
    try:
        event = paystack.Webhook.construct_event(
            payload, sig_header, settings.PAYSTACK_WEBHOOK_SECRET
        )
    except ValueError:
        return JsonResponse({'status': 'invalid payload'}, status=400)
    except paystack.error.SignatureVerificationError:
        return JsonResponse({'status': 'invalid signature'}, status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        order_id = session['client_reference_id']
        order = Order.objects.get(id=order_id)
        order.status = 'PROCESSING'
        order.save()
        Payment.objects.create(
            order=order,
            paystack_charge_id=session['payment_intent'],
            amount=Decimal(session['amount_total'] / 100),
            status='succeeded'
        )
    return JsonResponse({'status': 'success'})