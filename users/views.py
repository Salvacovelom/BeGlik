from django.shortcuts import render
from rest_framework.views import APIView
from utils.api_response import get_failed_response, get_successful_response, get_paginated_queryset, \
    get_paginated_response_structure
from rest_framework import status
from users.serializers import UserSerializer, UserCompanySerializer, AddressSerializer, DocumentSerializer, GroupSerializer
from authentication.models import User
from django.contrib.auth.models import Group
from django.contrib.postgres.search import SearchVector, SearchQuery
from django.db.models import Q, F, Count
from rest_framework.permissions import IsAuthenticated
from users.permissions import UserViewPermission, GroupViewPermission, UserAllViewPermission
from notifications.services.email import send_email_to_user
from glik.constants import GROUPS
from django.db import transaction
from users.models import UserDocument, Address
from django.utils.translation import gettext as _

# ================= #
#    User views     #
# ================= #

# public endpoint
class CustomerUserView(APIView):
  def post(self, request):     
    data = request.data.copy()
    # add user to customer group
    data['groups'] = [GROUPS['CUSTOMER']['id']]
    # serialize user
    user_serializer = UserSerializer(data=data)

    # Serializer validation
    if not user_serializer.is_valid():
      return get_failed_response(errors=user_serializer.errors, message=_("Validation error"))
      
    # transaction
    with transaction.atomic():
      user = user_serializer.save()
      user_id = user.id
      return get_successful_response(message=_("User created successfully"), status_code=status.HTTP_201_CREATED, data={"id": user_id})

class UserView(APIView):
  permission_classes = [IsAuthenticated, UserViewPermission]

  def get(self, request, id):
    """
    This method is used to get the user information
    """
    try: 
      queryset = User.objects.get(id=id)
      user_serializer = UserSerializer(queryset)
      return get_successful_response(data=user_serializer.data, message=_("User information"))
    except User.DoesNotExist:
      return get_failed_response(message=_("User not found"), status_code=status.HTTP_404_NOT_FOUND)

  def patch(self, request, id):
    """
    This method is used to update the user information
    """
    queryset = User.objects.get(id=id)
    data = request.data.copy()
    user_serializer = UserSerializer(queryset, data=data, partial=True)

    # Serializer validation
    if not user_serializer.is_valid():
      return get_failed_response(errors=user_serializer.errors, message=_("Validation error"))
    
    user_serializer.save()
    return get_successful_response(data=user_serializer.data, message=_("User updated successfully"))

  def delete(self, request, id):
    """
    This method is used to delete the user information
    """
    # TODO: delete all the user information OR soft delete
    try: 
      User.objects.get(id=id).delete()
      return get_successful_response(message=_("User deleted successfully"))
    except User.DoesNotExist:
      return get_failed_response(message=_("User not found", status_code=status.HTTP_404_NOT_FOUND))

class UserAllView(APIView):
  permission_classes = [IsAuthenticated, UserAllViewPermission]

  def post(self, request):    
    """
    This method is used to create a user (admins and riders)
    """
    data = request.data.copy()
    user_serializer = UserSerializer(data=data)

    # Serializer validation
    if not user_serializer.is_valid():
      return get_failed_response(errors=user_serializer.errors, message=_("Validation error"))

    user_serializer.save()
    return get_successful_response(message=_("User created successfully"), status_code=status.HTTP_201_CREATED)
  
  def get(self, request):
    """
    This method is used to get all the users with 
    - pagination
    - ordering
    - filtering 
    - searching (full text search)
    """
    queryset = self.get_filtered_queryset(request)
    ordering = self.get_ordering(request)

    search_param = request.query_params.get('search', None)
    if search_param:
      query_object = User.objects.annotate(
          search=SearchVector('id', 'first_name', 'last_name', 'email', 'phone_number', 'CI', config='spanish')
      ).filter(queryset).filter(search=SearchQuery(search_param, config='spanish'))
    else:
      query_object = User.objects.filter(queryset)

    users = query_object.order_by(ordering)
    page_object = get_paginated_queryset(request, users)
    serialized_data = UserSerializer(page_object.object_list, many=True).data
    response = get_paginated_response_structure(page_object, serialized_data)

    return get_successful_response(data=response)
  
  @staticmethod
  def get_filtered_queryset(request):
      queryset = Q()

      # state_param = request.query_params.getlist('state', [])
      # if state_param and len(state_param) > 0:
      #     queryset.add(Q(current_state__in=state_param), Q.AND)

      # date_option_param = request.query_params.get('date_option', None)
      # created_date_start_param = request.query_params.get('created_date_start', None)
      # created_date_end_param = request.query_params.get('created_date_end', None)
      # if date_option_param:
      #     start_date, end_date = get_date_range(date_option_param, created_date_start_param, created_date_end_param)

      #     if start_date:
      #         queryset.add(Q(created_date__gte=start_date), Q.AND)
      #     if end_date:
      #         queryset.add(Q(created_date__lte=end_date), Q.AND)

      return queryset

  @staticmethod
  def get_ordering(request):
        default_ordering = '-id'
        ordering_param = request.query_params.get('ordering', None)
        sorting = ''

        if ordering_param and ordering_param[0] == '-':
            sorting = '-'
            ordering_param = ordering_param[1:]

        valid_ordering_filters = User._meta.fields 
        valid_ordering_filters = [field.name for field in valid_ordering_filters]

        if ordering_param and ordering_param in valid_ordering_filters:
            ordering_param = sorting + ordering_param
            return ordering_param

        return default_ordering

class SelfUserView(APIView):
  permission_classes = [IsAuthenticated]
  def get(self, request):
    """
    This method is used to get the user in the authentication token
    """
    user = request.user
    user_serializer = UserSerializer(user)
    return get_successful_response(data=user_serializer.data, message=_("User information"))

# ================ #
#  document views  #
# ================ #

class UserDocumentView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request, id):
    """
    This method is used to get the user document information
    """
    try:
      user = request.user
      user_document = user.documents.get(id=id)
      user_document_serializer = DocumentSerializer(user_document)
      return get_successful_response(data=user_document_serializer.data, message=_("User document information"))
    except UserDocument.DoesNotExist:
      return get_failed_response(message=_("User document not found"), status_code=status.HTTP_404_NOT_FOUND)

  def patch(self, request, id):
    """
    This method delete the user document information, and then create a new one
    """
    with transaction.atomic():
      # Delete old document
      try: 
        UserDocument.undeleted_objects.get(id=id).soft_delete()
      except UserDocument.DoesNotExist:
        return get_failed_response(message=_("User document not found", status_code=status.HTTP_404_NOT_FOUND))

      # Create new document
      data = request.data.copy()    
      data['user'] = request.user.id # get user id from request
      user_document_serializer = DocumentSerializer(data=data)

      # Serializer validation
      if not user_document_serializer.is_valid():
        return get_failed_response(errors=user_document_serializer.errors, message=_("Validation error"))

      user_document_serializer.save()
      return get_successful_response(message=_("User document information updated successfully"), status_code=status.HTTP_201_CREATED)

  def delete(self, request, id):
    """
    This method is used to delete a user document
    """
    try: 
      UserDocument.undeleted_objects.get(id=id).soft_delete()
      return get_successful_response(message=_("User document deleted successfully"))
    except UserDocument.DoesNotExist:
      return get_failed_response(message=_("User document not found"), status_code=status.HTTP_404_NOT_FOUND)

class UserDocumentAllView(APIView):
  permission_classes = [IsAuthenticated]

  def post(self, request):
    """
    This method is used to create a user document
    """
    data = request.data.copy()
    # get user id from request
    data['user'] = request.user.id
    user_document_serializer = DocumentSerializer(data=data)

    # Serializer validation
    if not user_document_serializer.is_valid():
        return get_failed_response(errors=user_document_serializer.errors, message=_("Validation error"))

    user_document_serializer.save()        
    return get_successful_response(message=_("User document information created successfully"), status_code=status.HTTP_201_CREATED, data=user_document_serializer.data)

  def get(self, request):
    """
    This method is used to get all the user documents
    """
    user = request.user
    user_documents = UserDocument.undeleted_objects.filter(user=user)
    user_documents_serializer = DocumentSerializer(user_documents, many=True)
    return get_successful_response(data=user_documents_serializer.data, message=_("User documents information"))

# ================ #
#  address views   #
# ================ #

class UserAddressView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request, id):
    """
    This method is used to get the user address information
    """
    try:
      user = request.user
      user_address = Address.undeleted_objects.get(id=id, user=user)
      user_address_serializer = AddressSerializer(user_address)
      return get_successful_response(data=user_address_serializer.data, message=_("User address information"))
    except Address.DoesNotExist:
      return get_failed_response(message=_("User address not found"), status_code=status.HTTP_404_NOT_FOUND)

  def patch(self, request, id):
    """
    This method delete the user address information, and then create a new one
    """
    with transaction.atomic():
      # Delete old address
      try: 
        Address.undeleted_objects.get(id=id).soft_delete()
      except Address.DoesNotExist:
        return get_failed_response(message=_("User address not found"), status_code=status.HTTP_404_NOT_FOUND)

      # Create new address
      data = request.data.copy()    
      data['user'] = request.user.id
      user_address_serializer = AddressSerializer(data=data)

      # Serializer validation
      if not user_address_serializer.is_valid():
        return get_failed_response(errors=user_address_serializer.errors, message=_("Validation error"))
      
      user_address_serializer.save()
      return get_successful_response(message=_("User address information updated successfully"), status_code=status.HTTP_201_CREATED)  

  def delete(self, request, id):
    """
    This method is used to delete a user address
    """
    try: 
      Address.undeleted_objects.get(id=id).soft_delete()
      return get_successful_response(message=_("User address deleted successfully"))
    except Address.DoesNotExist:
      return get_failed_response(message=_("User address not found"), status_code=status.HTTP_404_NOT_FOUND)

class UserAddressAllView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request):
    """
    This method is used to get all the user addresses
    """
    user = request.user
    user_addresses = Address.undeleted_objects.filter(user=user)
    user_addresses_serializer = AddressSerializer(user_addresses, many=True)
    return get_successful_response(data=user_addresses_serializer.data, message=_("User addresses information"))

  def post(self, request):
    """
    This method is used to create a user address
    """
    data = request.data.copy()
    # get user id from request
    data['user'] = request.user.id        
    user_address_serializer = AddressSerializer(data=data)

    # Serializer validation
    if not user_address_serializer.is_valid():
      return get_failed_response(errors=user_address_serializer.errors, message=_("Validation error"))

    user_address_serializer.save()
    return get_successful_response(message=_("User address information created successfully"), status_code=status.HTTP_201_CREATED)

# ================ #
#    Other views   #
# ================ #

class GroupView(APIView):
  permission_classes = [IsAuthenticated, GroupViewPermission]

  def get(self, request):
    """
    This method is used to get all the groups
    """
    groups = Group.objects.all()
    return get_successful_response(data=groups.values(), message=_("Groups information"))

  def post(self, request):
    """
    This method is used to create a group
    """
    data = request.data.copy()
    group_serializer = GroupSerializer(data=data)

    # Serializer validation
    if not group_serializer.is_valid():
      return get_failed_response(errors=group_serializer.errors, message=_("Validation error"))

    group_id = group_serializer.save().id
    return get_successful_response(message=_("Group created successfully"), status_code=status.HTTP_201_CREATED, data={"id": group_id})

class UserCompanyView(APIView):
  permission_classes = [IsAuthenticated]

  def post(self, request):
    """
    This method is used to create a user company
    """
    data = request.data.copy()
    # get user id from request
    data['user'] = request.user.id
    user_company_serializer = UserCompanySerializer(data=data)

    # Serializer validation
    if not user_company_serializer.is_valid():
      return get_failed_response(errors=user_company_serializer.errors, message=_("Validation error"))

    user_company_serializer.save()
    return get_successful_response(message=_("User company information created successfully"), status_code=status.HTTP_201_CREATED)
