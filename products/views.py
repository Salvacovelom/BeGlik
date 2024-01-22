from django.shortcuts import render
from rest_framework.views import APIView, View
from utils.api_response import get_failed_response, get_successful_response, get_paginated_queryset, \
    get_paginated_response_structure, custom_handler
from products.serializers import ProductSerializer, CategorySerializer, ProductImageSerializer
from products.models import Product, Category
from django.db.models import Q, F, Count
from django.contrib.postgres.search import SearchVector, SearchQuery
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from products.permissions import ProductViewPermission, CategoryViewPermission
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
from django.core.files.uploadedfile import InMemoryUploadedFile
from rest_framework.response import Response
from django.http import FileResponse
from products.models import ProductImage
from rest_framework import viewsets
from requests import ConnectionError
from exceptions.custom_exception import CustomException
from products.services.categoryService import CategoryService

# ============ #
#   Products   #
# ============ #

class ProductView(APIView):
  permission_classes = [IsAuthenticatedOrReadOnly, ProductViewPermission]

  def get(self, request, id):
    """
    This method is used to get the product information
    """
    try: 
      queryset = Product.objects.get(internal_id=id)
      serializer = ProductSerializer(queryset)
      return get_successful_response(data=serializer.data, message=_("Product information"))
    except Product.DoesNotExist:
      raise CustomException("Product not found", status.HTTP_404_NOT_FOUND)

  def patch(self, request, id):
    """
    This method is used to update the product information
    """
    try:
      queryset = Product.objects.get(internal_id=id)
      data = request.data.copy()
      serializer = ProductSerializer(queryset, data=data, partial=True)

      # Serializer validation
      serializer.is_valid( raise_exception=True )
      
      serializer.save()
      return get_successful_response(data=serializer.data, message=_("Product updated successfully"))
    except Product.DoesNotExist:
      raise CustomException("Product not found", status.HTTP_404_NOT_FOUND)

  def delete(self, request, id):
    """
    This method is used to delete the product information
    """
    try: 
      Product.objects.get(internal_id=id).delete()
      return get_successful_response(message=_("Product deleted successfully"))
    except Product.DoesNotExist:
      raise CustomException("Product not found", status.HTTP_404_NOT_FOUND)

class ProductAllView(APIView):
  permission_classes = [IsAuthenticatedOrReadOnly, ProductViewPermission]

  def post(self, request):    
    """
    This method is used to create a product
    """
    data = request.data.copy()
    serializer = ProductSerializer(data=data)

    # Serializer validation
    serializer.is_valid( raise_exception=True )

    id = serializer.save().internal_id
    return get_successful_response(message=_("Product created successfully"), status_code=status.HTTP_201_CREATED, data=id)
  
  def get(self, request):
    """
    This method is used to get all the products with 
    - pagination
    - ordering
    - filtering 
    - searching (full text search)
    """
    queryset = self.get_filtered_queryset(request)
    ordering = self.get_ordering(request)

    # search section
    search_param = request.query_params.get('search', None)
    if search_param:
        query_object = Product.objects.annotate(
            search=SearchVector('id', 'name', 'description', 'brand', config='spanish')
        ).filter(queryset) \
        .filter(search=SearchQuery(search_param, config='spanish'))
    else:
        query_object = Product.objects.filter(queryset)

    # variable to allow order products by the number of leases
    query_object = query_object.annotate(leases_count=Count('leases_products'))

    # ordering section
    products = query_object.order_by(ordering)

    # pagination section and response
    page_object = get_paginated_queryset(request, products)
    serialized_data = ProductSerializer(page_object.object_list, many=True).data
    response = get_paginated_response_structure(page_object, serialized_data)

    return get_successful_response(data=response)
    
  @staticmethod
  def get_filtered_queryset(request):
    queryset = Q()

    # category filter
    category_param = request.query_params.get('category', None)
    if category_param:
      queryset &= Q(category__id=category_param)

    # is featured filter
    is_featured_param = request.query_params.get('is_featured', None)
    if is_featured_param:
      queryset &= Q(is_featured=is_featured_param)

    return queryset

  @staticmethod
  def get_ordering(request):
    """
    To sort by any of the main fields of the model, you can use the ordering parameter.
    They have to be in snake case.
    Example: /api/products/all?ordering=-id

    To sort by the number of leases, you can use the ordering parameter
    Example: /api/products/all?ordering=-leases_count
    """
    default_ordering = '-id'
    ordering_param = request.query_params.get('ordering', None)
    sorting = ''

    if ordering_param and ordering_param[0] == '-':
      sorting = '-'
      ordering_param = ordering_param[1:]

    valid_ordering_filters = Product._meta.fields 
    valid_ordering_filters = [field.name for field in valid_ordering_filters]
    valid_ordering_filters.append('leases_count')

    # best sellers ordering

    if ordering_param and ordering_param in valid_ordering_filters:
      ordering_param = sorting + ordering_param
      return ordering_param

    return default_ordering

class ProductImageUploadView(viewsets.ModelViewSet):
  permission_classes = [IsAuthenticatedOrReadOnly, ProductViewPermission]
  serializer_class = ProductImageSerializer
  queryset = ProductImage.objects.all()

# ============ #
#  Categories  #
# ============ #

class CategoryView(APIView):
  permission_classes = [IsAuthenticatedOrReadOnly, CategoryViewPermission]

  def get(self, request, id):
    """
    This method is used to get the category information
    """
    try:
      queryset = Category.objects.get(id=id)
      serializer = CategorySerializer(queryset)
      return get_successful_response(data=serializer.data, message=_("Category information"))
    except Category.DoesNotExist:
      return get_failed_response(message=_("Category not found"), status_code=status.HTTP_404_NOT_FOUND)

  def patch(self, request, id):
    """
    This method is used to update the category information
    """
    try:
      queryset = Category.objects.get(id=id)
      data = request.data.copy()
      serializer = CategorySerializer(queryset, data=data, partial=True)

      # Serializer validation
      serializer.is_valid( raise_exception=True )
      
      serializer.save()
      return get_successful_response(data=serializer.data, message=_("Category updated successfully"))
    except Category.DoesNotExist:
      return get_failed_response(message=_("Category not found"), status_code=status.HTTP_404_NOT_FOUND)

  def delete(self, request, id):
    """
    This method is used to delete the category information
    """
    try: 
      CategoryService.delete_category(id)
      return get_successful_response(message=_("Category deleted successfully"))
    except Category.DoesNotExist:
      return get_failed_response(message=_("Category not found"), status_code=status.HTTP_404_NOT_FOUND)

class CategoryAllView(APIView):
  permission_classes = [IsAuthenticatedOrReadOnly, CategoryViewPermission]

  def post(self, request):
    """
    This method is used to create a category
    """
    data = request.data.copy()
    serializer = CategorySerializer(data=data)
    serializer.is_valid( raise_exception=True )

    category = serializer.save()
    return get_successful_response(message=_("Category created successfully"), status_code=status.HTTP_201_CREATED, data=category.id)

  def get(request, id):
    """
    This method is used to get all the categories
    """
    try:
      # the child array is empty 
      queryset = Category.objects.filter( children__isnull=True )
      serialized_data = CategorySerializer(queryset, many=True).data
      return get_successful_response(data=serialized_data)
    except Category.DoesNotExist:
      return get_failed_response(message=_("Categories not found"), status_code=status.HTTP_404_NOT_FOUND)