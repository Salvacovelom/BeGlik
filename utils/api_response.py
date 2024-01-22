from django.core.paginator import Page, Paginator
from rest_framework import status
from rest_framework.response import Response
from glik.constants import PAGE_SIZE_DEFAULT, REQUEST_SUCCESSFUL, REQUEST_UNSUCCESSFUL
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

def get_page_params(request):
  page = request.GET.get('page', 1)
  page_size = request.GET.get('page_size', PAGE_SIZE_DEFAULT)

  return page, page_size


def get_paginated_queryset(request, queryset):
  page, page_size = get_page_params(request)
  paginator = Paginator(queryset, page_size)
  page_object = paginator.get_page(page)

  return page_object


def get_paginated_response_structure(page_object, serialized_data):
  response_structure = {
      'current_page': page_object.number,
      'page_size': page_object.paginator.per_page,
      'total_elements': page_object.paginator.count,
      'total_pages': page_object.paginator.num_pages,
      'results': serialized_data,
  }

  return response_structure


def get_successful_response(message=REQUEST_SUCCESSFUL, data=None, status_code=status.HTTP_200_OK):
  if data is None:
      data = []

  return Response({
      'message': message,
      'data': data,
  }, status=status_code)


def get_failed_response(message=REQUEST_UNSUCCESSFUL, errors=None, status_code=status.HTTP_400_BAD_REQUEST):
  if errors is None:
      errors = []

  return Response({
      'message': message,
      'errors': errors,
  }, status=status_code)

def custom_handler(exception, request, *args, **kwargs):        
  if isinstance(exception, serializers.ValidationError):
    return get_failed_response(errors=exception.detail, message=_("Validation error"), status_code=status.HTTP_400_BAD_REQUEST)
  return get_failed_response(message=_("Internal server error"), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
