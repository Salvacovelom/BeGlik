from django.db import models
from glik.constants import LEASE_WEEKS_PERIODS

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True, null=False)
    parent = models.ForeignKey('self', null=True, on_delete=models.SET_NULL, related_name='children')

class Product(models.Model):
    id = models.AutoField(primary_key=True)
    internal_id = models.CharField(max_length=64, unique=True, null=False)
    name = models.CharField(max_length=50, unique=True, null=False)
    description = models.TextField(null=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', null=False)
    stock = models.PositiveBigIntegerField(null=False)
    lease_price = models.PositiveBigIntegerField(null=False)
    initial_fee = models.PositiveBigIntegerField(null=False)
    cash_price = models.PositiveBigIntegerField(null=False)
    brand = models.CharField(max_length=50, null=False)
    extra = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)

    @property
    def lease_options(self):
        ans = {}
        for weeks in LEASE_WEEKS_PERIODS:
            ans[weeks] = {
                'initial_fee': self.initial_fee,
                'weekly_fee': self.lease_price / weeks,
                'total': self.initial_fee + self.lease_price / weeks * weeks
            }
        return ans
    
    def get_images(self):
        product_images = self.images.all()        
        return [ image.image.url for image in product_images ]

class ProductImage(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', null=False)
    image = models.ImageField(upload_to='product_images', null=True) # TODO: Make migration for this
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.image.url + " " + self.product.name
