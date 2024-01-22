from rest_framework import serializers
from users.models import UserContact, User, UserCompany, Company, Address, UserDocument, CustomerUser
from django.contrib.auth.models import Group
from django.db import transaction
from glik.constants import DOCUMENT_TYPES
from django.utils.translation import gettext_lazy as _
from users.services.document import DocumentService

# ===================== #
#  Models Serializers   #
# ===================== #

class CompanySerializer(serializers.ModelSerializer):
  web_page = serializers.CharField(required=False)
  instagram = serializers.CharField(required=False)
  facebook = serializers.CharField(required=False)
  address = serializers.CharField(required=False)
  class Meta:
    model = Company
    fields = ('__all__')

class UserContactSerializer(serializers.ModelSerializer):
  name = serializers.CharField(required=True)
  phone_number = serializers.CharField(required=True)
  email = serializers.EmailField(required=True)
  address = serializers.CharField(required=True)
  relationship = serializers.CharField(required=True)

  class Meta:
    model = UserContact
    fields = ('__all__')

class UserCompanySerializer(serializers.ModelSerializer):
  user = serializers.PrimaryKeyRelatedField(many=False, queryset=User.objects.all())
  company = CompanySerializer(many=False)
  boss = UserContactSerializer(many=False, required = False)

  class Meta:
    model = UserCompany
    fields = ('__all__')

  # ==================== #
  #  Custom operations   #
  # ==================== #
  
  def create(self, validated_data):
    if 'company' in validated_data:
      company_data = validated_data.pop('company')
      company, _ = Company.objects.get_or_create(**company_data)
      validated_data['company'] = company
    
    if 'boss' in validated_data:
      boss_data = validated_data.pop('boss')
      boss, _ = UserContact.objects.get_or_create(**boss_data)
      validated_data['boss'] = boss
        
    user_company = UserCompany(**validated_data)
    user_company.save()
    return user_company

  def update(self, instance, validated_data):
    if 'company' in validated_data:
      company_data = validated_data.pop('company')
      company, _ = Company.objects.get_or_create(**company_data)
      validated_data['company'] = company
    
    if 'boss' in validated_data:
      boss_data = validated_data.pop('boss')
      boss, _ = UserContact.objects.get_or_create(**boss_data)
      validated_data['boss'] = boss
    
    instance.update(**validated_data)
    instance.save()
    return instance

# ========================= # 
#    Users of the system    #
# ========================= #

class UserCustomSerializer(serializers.ModelSerializer):
  user = serializers.PrimaryKeyRelatedField(many=False, queryset=User.objects.all(), required=False)
  contact_user_reference = UserContactSerializer(many=False, required=False)
  class Meta:
    model = CustomerUser
    fields = ('__all__')
    depth = 1
  
  # ==================== #
  #  Custom operations   #
  # ==================== #

  def create(self, validated_data):        
    validated_data['score'] = 0
    new_contact_user_reference = None 
    if 'contact_user_reference' in validated_data:
      # create user contact with the serializer
      contact_user_reference_data = validated_data.pop('contact_user_reference')
      contact_user_reference_serializer = UserContactSerializer(data=contact_user_reference_data)
      contact_user_reference_serializer.is_valid(raise_exception=True)
      new_contact_user_reference = contact_user_reference_serializer.save()

    user = CustomerUser(**validated_data)
    if new_contact_user_reference:
      user.contact_user_reference = new_contact_user_reference
    user.save()
    return user
  
  def update(self, instance, validated_data):
    if 'score' in validated_data:
      # This is because the score is calculated in the backend
      raise serializers.ValidationError(_("score can't be updated"))
    if 'contact_user_reference' in validated_data:
      # update user contact with the serializer
      contact_user_reference_data = validated_data.pop('contact_user_reference')
      contact_user_reference = instance.contact_user_reference
      contact_user_reference_serializer = UserContactSerializer(contact_user_reference, data=contact_user_reference_data, partial=True)
      contact_user_reference_serializer.is_valid(raise_exception=True)
      contact_user_reference_serializer.save()
    
    instance.update(**validated_data)
    instance.save()
    return instance

class UserSerializer(serializers.ModelSerializer):
  email = serializers.EmailField(required=True)
  password = serializers.CharField(required=True, write_only=True)
  country_user_id = serializers.CharField(required=True)
  username = serializers.CharField(required=True)    
  groups = serializers.ManyRelatedField(required=False, child_relation=serializers.PrimaryKeyRelatedField(queryset=Group.objects.all()))
  customer = UserCustomSerializer(many=False, required=False)

  class Meta:
    model = User
    fields = ('__all__')
    depth = 1

  # ==================== #
  #  Custom validations  #
  # ==================== #

  # TODO: Validate phone number format

  def validate_email(self, value):
    if User.objects.filter(email=value).exists():
      raise serializers.ValidationError(_("Email already exists"))
    return value
  
  def validate_username(self, value):
    if User.objects.filter(username=value).exists():
      raise serializers.ValidationError(_("Username already exists"))
    return value

  def validate_country_user_id(self, value):
    if User.objects.filter(country_user_id=value).exists():
      raise serializers.ValidationError(_("country_user_id already exists"))
    return value

  # ==================== #
  #  Custom operations   #
  # ==================== #
  
  def create(self, validated_data):
    customer_data = validated_data.pop('customer',None)
    # Get the groups and remove it from the validated data    
    groups = validated_data.pop('groups', [])    

    with transaction.atomic():
      validated_data['is_active'] = True
      user = User(**validated_data)
      user.set_password(validated_data['password'])
      user.save()
      user.groups.set(groups)

      if customer_data:
        # create the one to one relationship using the serializer
        customer_data['user'] = user.id
        customer_serializer = UserCustomSerializer(data=customer_data)
        customer_serializer.is_valid(raise_exception=True)
        customer_serializer.save()        

      return user

  def update(self, instance, validated_data):    
    if 'country_user_id' in validated_data:
      # This is because the country_user_id have to be the same in all the system
      # Specially in the payments 
      raise serializers.ValidationError(_("country_user_id can't be updated"))
    
    if 'password' in validated_data:
      instance.set_password(validated_data['password'])        

    if 'customer' in validated_data:
      # update the one to one relationship using the serializer
      customer_data = validated_data.pop('customer')
      customer = instance.customer
      customer_serializer = UserCustomSerializer(customer, data=customer_data, partial=True)
      customer_serializer.is_valid(raise_exception=True)
      customer_serializer.save()
    
    # Get the groups and remove it from the validated data
    groups = validated_data.pop('groups', [])    
    
    with transaction.atomic():
      instance.update(**validated_data)
      instance.groups.set(groups)
      instance.save()
      return instance

  def delete(self, instance):
    instance.delete()
    return instance

# ==================== # 
#  Other serializers   #
# ==================== #

class AddressSerializer(serializers.ModelSerializer):
  user = serializers.PrimaryKeyRelatedField(many=False, queryset=User.objects.all(), required=False)
  created_at = serializers.DateTimeField(read_only=True, required=False)
  is_deleted = serializers.BooleanField(required=False, default=False, read_only=True)

  class Meta:
    model = Address
    fields = ('__all__')

class DocumentSerializer(serializers.ModelSerializer):
  user = serializers.PrimaryKeyRelatedField(many=False, queryset=User.objects.all(), required=False)
  created_at = serializers.DateTimeField(read_only=True, required=False)
  is_deleted = serializers.BooleanField(required=False, default=False, read_only=True)

  class Meta:
    model = UserDocument
    fields = ('__all__')
  
  # ==================== #
  #  Custom validations  #
  # ==================== #

  def validate_name(self, value):
    if value not in DOCUMENT_TYPES:
      error_message = _("Document type not allowed, the valid types are: ")
      raise serializers.ValidationError(error_message+" "+str(DOCUMENT_TYPES))
    return value
  
  # ==================== #
  #  Custom operations   #
  # ==================== #

  def create(self, validated_data):
    validated_data['is_deleted'] = False 
    user_document = UserDocument(**validated_data)

    with transaction.atomic():
      # Create name of the document
      user_id = validated_data['user'].id
      user_document.document.name = DocumentService.get_internal_name( user_id, validated_data['name'] )

      user_document.save()
      return user_document

class GroupSerializer(serializers.ModelSerializer):
  class Meta:
    model = Group
    fields = ('__all__')