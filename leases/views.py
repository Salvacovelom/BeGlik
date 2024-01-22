from django.shortcuts import render
from rest_framework.views import APIView
from utils.api_response import get_successful_response, get_failed_response \
    , get_paginated_queryset, get_paginated_response_structure
from rest_framework import status
from leases.serializers import LeaseSerializer, CreateLeaseSerializer, LoanGrantorSerializer
from leases.models import Lease, LoanGrantor
from django.db.models import Q, F, Count
from django.contrib.postgres.search import SearchVector, SearchQuery
from rest_framework.permissions import IsAuthenticated
from leases.permissions import LeaseViewPermission, LeaseAllViewPermission, LoanGrantorViewPermission
from django.utils.translation import gettext_lazy as _
from exceptions.custom_exception import CustomException
import leases.services.lease as lease_service
from glik.constants import LEASES_STATUS
from products.serializers import ProductSerializer
from products.models import Product
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from users.models import Company
from users.serializers import CompanySerializer

# ========== #
#   Leases   #
# ========== #

class LeaseView(APIView):
  permission_classes = [IsAuthenticated, LeaseViewPermission]

  def get(self, request, id):
    """
    This method is used to get the lease information
    """
    try: 
      queryset = Lease.objects.get(id=id)
      serializer = LeaseSerializer(queryset)
      return get_successful_response(data=serializer.data, message="Lease information")
    except Lease.DoesNotExist:
      return get_failed_response(message=_("Lease not found"), status_code=status.HTTP_404_NOT_FOUND)

class LeaseAllView(APIView):  
  permission_classes = [IsAuthenticated, LeaseAllViewPermission]

  def post(self, request):
    """
    This method is used to create a new lease
    """

    # Validate user documents
    # can_create, errorMessage = request.user.can_create_leases
    # if not can_create:
    #   raise CustomException(message=errorMessage, status_code=status.HTTP_400_BAD_REQUEST)

    data = request.data.copy()
    # get user id from request
    data['lease']['user'] = request.user.id
    data['lease']['status'] = LEASES_STATUS.PENDING_APPROVAL.value
    serializer = CreateLeaseSerializer(data=data)

    # Serializer validation
    if not serializer.is_valid():
      return get_failed_response(errors=serializer.errors, message=_("Validation error"))

    lease_id = serializer.save()
    return get_successful_response(data=lease_id, message=_("Lease created successfully"))

  def get(self, request):
    """
    This method is used to get all the leases with 
    - pagination
    - ordering
    - filtering 
    - searching (full text search)
    """
    queryset = self.get_filtered_queryset(request)
    ordering = self.get_ordering(request)
    query_object = self.get_query_object(request, queryset)
    leases = query_object.order_by(ordering)

    page_object = get_paginated_queryset(request, leases)
    serialized_data = LeaseSerializer(page_object.object_list, many=True).data
    response = get_paginated_response_structure(page_object, serialized_data)

    return get_successful_response(data=response)
  
  @staticmethod
  def get_query_object(request, queryset):
    search_param = request.query_params.get('search', None)
    if search_param:
        query_object = Lease.objects.annotate(
            search=SearchVector('id', 'lease_reason')
        ).filter(queryset).filter(search=SearchQuery(search_param, config='spanish'))
    else:
        query_object = Lease.objects.filter(queryset)
    return query_object
    
  @staticmethod
  def get_filtered_queryset(request):
    queryset = Q()

    # Filter by user
    user_id = request.query_params.get('user', None)
    if user_id:
      queryset &= Q(user=user_id)
    
    return queryset

  @staticmethod
  def get_ordering(request):
    default_ordering = '-id'
    ordering_param = request.query_params.get('ordering', None)
    sorting = ''

    if ordering_param and ordering_param[0] == '-':
      sorting = '-'
      ordering_param = ordering_param[1:]

    valid_ordering_filters = Lease._meta.fields 
    valid_ordering_filters = [field.name for field in valid_ordering_filters]

    if ordering_param and ordering_param in valid_ordering_filters:
      ordering_param = sorting + ordering_param
      return ordering_param

    return default_ordering

class LeaseStatusView(APIView):
  permission_classes = [IsAuthenticated, LeaseViewPermission]

  def put(self, request, id):
    """
    This method is used to update the status of a lease
    """
    # Validation 
    if 'new_status' not in request.data:
      raise CustomException(message="new_status is required", status_code=400)
    # Update the status
    new_status = request.data['new_status']      
    lease_service.update_lease_status(new_status, id)
    return get_successful_response(message="Lease status updated successfully")
  

# ================= #
#   User Leases     #
# ================= #

class UserLeasesView(APIView):  
  permission_classes = [IsAuthenticated]

  def get(self, request, id):
    """
    This method is used to get the lease information
    """
    try: 
      queryset = Lease.objects.get(id=id, user=request.user)
      serializer = LeaseSerializer(queryset)
      return get_successful_response(data=serializer.data, message="Lease information")
    except Lease.DoesNotExist:
      return get_failed_response(message=_("Lease not found"), status_code=status.HTTP_404_NOT_FOUND)

class UserLeasesAllView(APIView):  
  permission_classes = [IsAuthenticated]

  def get(self, request):
    """
    This method is used to get all the leases with 
    - pagination
    - ordering
    - filtering 
    - searching (full text search)
    """
    queryset = LeaseAllView.get_filtered_queryset(request)
    ordering = LeaseAllView.get_ordering(request)
    query_object = LeaseAllView.get_query_object(request, queryset)
    query_object = query_object.filter(user=request.user) # Filter by user
    leases = query_object.order_by(ordering)
    
    page_object = get_paginated_queryset(request, leases)
    serialized_data = LeaseSerializer(page_object.object_list, many=True).data
    response = get_paginated_response_structure(page_object, serialized_data)

    for lease in response['results']:
      queryset = Product.objects.get(id=int(lease['product']))
      serializer = ProductSerializer(queryset).data
      lease['product'] = serializer
    
    return get_successful_response(data=response, message="Leases information")

# ================= #
#   Loan Grantor    #
# ================= #

class LoanGrantorView(viewsets.ModelViewSet):
  permission_classes = [IsAuthenticatedOrReadOnly, LoanGrantorViewPermission]
  serializer_class = LoanGrantorSerializer
  queryset = LoanGrantor.objects.all()

class LoanGrantorCompanyView(viewsets.ModelViewSet):
  permission_classes = [IsAuthenticatedOrReadOnly, LoanGrantorViewPermission]
  serializer_class = CompanySerializer
  queryset = Company.objects.all()