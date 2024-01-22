import logging
from rest_framework.views import exception_handler
from django.http import JsonResponse
from requests import ConnectionError
from exceptions.custom_exception import CustomException
from utils.api_response import get_failed_response
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework import status

def custom_exception_handler(exc, context):
  # Call REST framework's default exception handler first
  response = exception_handler(exc, context)

  # Check in the list of exceptions that we handle
  if isinstance(exc, CustomException):
    translated_message = _(exc.message)
    return get_failed_response(message=translated_message, errors=exc.errors, status_code=exc.status_code)
  
  if isinstance(exc, serializers.ValidationError):
    return get_failed_response(errors=exc.detail, message=_("Validation error"), status_code=status.HTTP_400_BAD_REQUEST)

  # returns response as handled normally by the framework
  return response