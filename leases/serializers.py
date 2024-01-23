from rest_framework import serializers
from leases.models import Lease, LoanGrantor, PaymentDelay, UserDocumentsLease
from users.models import User, Address, Company, UserDocument
from products.models import Product
from users.serializers import CompanySerializer
from django.db import transaction
from glik.constants import LEASES_TYPES

# ===================== #
#  Models Serializers   #
# ===================== #

class LeaseSerializer(serializers.ModelSerializer):
  user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
  product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
  address = serializers.PrimaryKeyRelatedField(queryset=Address.objects.all())
  rider = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), allow_null=True, required=False)
  loan_grantor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=False)
  created_at = serializers.DateTimeField(required=False)
  next_payment_date = serializers.DateTimeField(required=False)
  type = serializers.ChoiceField(choices=LEASES_TYPES, required=True)

  class Meta:
    model = Lease    
    fields = [
      'id', 
      'status', 
      'created_at', 
      'user', 
      'user_score', 
      'product', 
      'full_product_price', 
      'initial_fee', 
      'monthly_fee', 
      'fees_number', 
      'address', 
      'rider', 
      'loan_grantor', 
      'lease_reason',
      'payments',
      'next_payment_date',
      'type',
      'weekly_income'
    ]
    depth = 3

class LoanGrantorSerializer(serializers.ModelSerializer):
  first_name = serializers.CharField(max_length=50, required=True, min_length=2)
  last_name = serializers.CharField(max_length=50, required=True, min_length=2)
  relationship = serializers.CharField(max_length=50, required=True, min_length=2)
  phone_number = serializers.CharField(max_length=50, required=True, min_length=2)
  email = serializers.EmailField(max_length=50, required=True, min_length=2)  
  address_room = serializers.CharField(max_length=50, required=True, min_length=2)
  land_line_number = serializers.CharField(max_length=50, required=True, min_length=2)
  company = serializers.PrimaryKeyRelatedField(queryset=Company.objects.all(), required=False)
  
  class Meta:
    model = LoanGrantor
    fields = ('__all__')

class UserDocumentsLeaseSerializer(serializers.ModelSerializer):
  user_document = serializers.PrimaryKeyRelatedField(queryset=UserDocument.objects.all())
  # lease = serializers.PrimaryKeyRelatedField(queryset=Lease.objects.all(), required=False)
  
  class Meta:
    model = UserDocumentsLease
    fields = ['user_document']

class PaymentDelaySerializer(serializers.ModelSerializer):
  created_at = serializers.DateTimeField()
  lease = serializers.PrimaryKeyRelatedField(queryset=Lease.objects.all())
  class Meta:
    model = PaymentDelay
    fields = ('__all__')

# ===================== #
#  Custom Serializers   #
# ===================== #

class CreateLeaseSerializer(serializers.Serializer):
  company = CompanySerializer()
  loan_grantor = LoanGrantorSerializer()
  lease = LeaseSerializer()  

  def create(self, validated_data):
    with transaction.atomic():
      # Get data from validated data
      company_data = validated_data.pop('company')
      loan_grantor_data = validated_data.pop('loan_grantor')
      lease_data = validated_data.pop('lease')
      # Create company of the loan grantor
      company = CompanySerializer.create(CompanySerializer(), validated_data=company_data)
      # Create loan grantor of the lease
      loan_grantor_data['company'] = company
      loan_grantor = LoanGrantorSerializer.create(LoanGrantorSerializer(), validated_data=loan_grantor_data)
      # Create lease
      lease_data['loan_grantor'] = loan_grantor
      lease = LeaseSerializer.create(LeaseSerializer(), validated_data=lease_data)  
      # Create user document of the lease
      # TODO: Take current active documents of the user and associate them with the lease
      return lease.id

