from rest_framework import serializers
from products.models import Product, Category, ProductImage
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.db import transaction
from products.services.product import ProductService
from utils.Serializer_message import SerializerMessage

# ===================== #
#  Models Serializers   #
# ===================== #

class ProductSerializer(serializers.ModelSerializer):
  category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
  description = serializers.CharField(required=True, min_length=3, max_length=500)
  name = serializers.CharField(required=True, min_length=3, max_length=50)
  stock = serializers.IntegerField(required=True, min_value=0)
  lease_price = serializers.IntegerField(required=True, min_value=0)
  initial_fee = serializers.IntegerField(required=True, min_value=0)
  cash_price = serializers.IntegerField(required=True, min_value=0)
  brand = serializers.CharField(required=True, min_length=3, max_length=50)
  internal_id = serializers.CharField(required=False, min_length=3, max_length=64)
  created_at = serializers.DateTimeField(required=False)
  lease_options = serializers.JSONField(required=False)  
  images = serializers.SerializerMethodField()  

  class Meta:
    model = Product
    fields = ('__all__')
  
  # ===================== #
  #  Custom validations   #
  # ===================== #

  def get_images(self, obj): return obj.get_images()

  def validate_name(self, value):
    if Product.objects.filter(name=value).exists():
      raise serializers.ValidationError(_("Product name already exists"))
    # search internal id
    if Product.objects.filter(internal_id=slugify(value)).exists():
      raise serializers.ValidationError(_("Product name already exists"))
    return value

  # ================== #
  # Custom operation   #
  # ================== #

  def create(self, validated_data):
    validated_data['internal_id'] = slugify(validated_data['name'])

    product = Product.objects.create(**validated_data)
    return product

class CategorySerializer(serializers.ModelSerializer):
  name = serializers.CharField(required=True, min_length=3, max_length=50)  
  class Meta:
    model = Category
    fields = ('__all__')
  
  # ===================== #
  #  Custom validations   #
  # ===================== #

  def validate_name(self, value):
    if Category.objects.filter(name=value).exists():
      raise serializers.ValidationError(_("Category name already exists"))
    return value

class ProductImageSerializer(SerializerMessage, serializers.ModelSerializer):
  product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
  image = serializers.ImageField(required=True)
  
  class Meta:
    model = ProductImage
    fields = ('__all__')

  # =================== #
  #  Custom operations  #
  # =================== #

  def create(self, validated_data):
    product = validated_data['product']
    image = validated_data['image']

    with transaction.atomic():
      last_product_image = ProductService.get_last_product_image(product) 
      last_product_image_number = int(last_product_image.split('_')[-1]) if last_product_image else 0
      image.name = product.internal_id + "_" + str(last_product_image_number + 1)
      product_image = ProductImage.objects.create(image=image, product=product)
      return product_image 
  
  def update(self, instance, validated_data):
    # delete current image and create a new one
    instance.image.delete()
    return self.create(validated_data)  
  
