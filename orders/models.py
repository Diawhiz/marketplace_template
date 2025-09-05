from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
from decimal import Decimal

class Order(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    stripe_payment_id = models.CharField(max_length=100, blank=True)

    def save(self, *args, **kwargs):
        if not self.tax_amount:
            tax_rate = TaxRate.objects.filter(region='default').first() or Decimal('0.08')
            self.tax_amount = self.total_price * tax_rate.rate
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} by {self.user.email}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"
    
class TaxRate(models.Model):
    region = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2)  # e.g., 0.08 for 8%

    def __str__(self):
        return f"{self.region}: {self.rate}%"