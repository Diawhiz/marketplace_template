from django.urls import path
from django.shortcuts import render
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout-session/<int:order_id>/', views.create_checkout_session, name='create_checkout_session'),
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('success/', lambda x: render(x, 'orders/success.html'), name='success'),
    path('cancel/', lambda x: render(x, 'orders/cancel.html'), name='cancel'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
]