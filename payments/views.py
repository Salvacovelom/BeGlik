from django.shortcuts import render
from rest_framework.views import APIView
from utils.api_response import get_successful_response, get_failed_response \
    , get_paginated_queryset, get_paginated_response_structure
from rest_framework import status
from payments.serializers import PaymentSerializer
from payments.models import Payment
from django.db.models import Q
from django.contrib.postgres.search import SearchVector, SearchQuery
from rest_framework.permissions import IsAuthenticated
from payments.permissions import PaymentViewPermission
from django.utils.translation import gettext as _
from glik.constants import PAYMENTS_STATUS
import payments.services.payment as payment_service

# =========== #
#   Payment   #
# =========== #

class LeasePaymentView(APIView):
  permission_classes = [IsAuthenticated]

  def post(self, request, id):
    """
    This method is used to create a payment
    """
    data = request.data.copy()
    # get lease id from params
    data['lease'] = id
    # get user id from request
    data['user'] = request.user.id
    # state
    data['state'] = 'created'
    data['status'] = PAYMENTS_STATUS.PENDING.value
    serializer = PaymentSerializer(data=data)

    # Serializer validation
    if not serializer.is_valid():
        return get_failed_response(errors=serializer.errors, message=_("Validation error"))

    serializer.save()
    return get_successful_response(message=_("Payment created successfully"), status_code=status.HTTP_201_CREATED)

class PaymentAllView(APIView):
  permission_classes = [IsAuthenticated, PaymentViewPermission]

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

    search_param = request.query_params.get('search', None)
    if search_param:
        query_object = Payment.objects.annotate(
            search=SearchVector('id', 'type', config='spanish')
        ).filter(queryset).filter(search=SearchQuery(search_param, config='spanish'))
    else:
        query_object = Payment.objects.filter(queryset)

    products = query_object.order_by(ordering)
    page_object = get_paginated_queryset(request, products)
    serialized_data = PaymentSerializer(page_object.object_list, many=True).data
    response = get_paginated_response_structure(page_object, serialized_data)

    return get_successful_response(data=response)
    
  @staticmethod
  def get_filtered_queryset(request):
    queryset = Q()

    state = request.query_params.get('state', [])
    if state:
      queryset &= Q(state__in=state)
    
    lease = request.query_params.get('lease', None)
    if lease:
      queryset &= Q(lease=lease)
    
    user = request.query_params.get('user', None)
    if user:
      queryset &= Q(user=user)
        
    return queryset

  @staticmethod
  def get_ordering(request):
    default_ordering = '-id'
    ordering_param = request.query_params.get('ordering', None)
    sorting = ''

    if ordering_param and ordering_param[0] == '-':
      sorting = '-'
      ordering_param = ordering_param[1:]

    valid_ordering_filters = Payment._meta.fields 
    valid_ordering_filters = [field.name for field in valid_ordering_filters]

    if ordering_param and ordering_param in valid_ordering_filters:
      ordering_param = sorting + ordering_param
      return ordering_param

    return default_ordering

class PaymentStatusView(APIView):
  permission_classes = [IsAuthenticated, PaymentViewPermission]

  def put(self, request, id):
    """
    This method is used to update a payment status
    """
    if 'new_status' not in request.data:
      return get_failed_response(message=_("new_status is required"))
    
    payment_service.update_payment_status(request.data['new_status'], id)
    return get_successful_response(message=_("Payment updated successfully"))