from django.db import models

class ProductCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(ProductCategory, on_delete=models.SET_NULL, null=True)
    inventory = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='products/', blank=True)

    def __str__(self):
        return self.name