from django.db import models
from users.models import User, Address, UserDocument, Company
from products.models import Product
import datetime
from glik.constants import LEASES_TYPES, PAYMENTS_STATUS

class LoanGrantor(models.Model):
  id = models.AutoField(primary_key=True)
  first_name = models.CharField(max_length=50)
  last_name = models.CharField(max_length=50)
  relationship = models.CharField(max_length=50)
  phone_number = models.CharField(max_length=50)
  email = models.CharField(max_length=50)
  address_room = models.CharField(max_length=50)
  land_line_number = models.CharField(max_length=50)
  company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='loan_grantors_company')

  """
  JSON representation of the model.
  {
    "first_name": "Loan grantor first name",
    "last_name": "Loan grantor last name",
    "relationship": "Loan grantor relationship",
    "phone_number": "Loan grantor phone number",
    "email": "Loan grantor email",
    "address_room": "Loan grantor address room",
    "land_line_number": "Loan grantor land line number",
    "company": 1
  }
  """

class Lease(models.Model):
  id = models.AutoField(primary_key=True)
  status = models.CharField(max_length=50)
  created_at = models.DateTimeField(auto_now_add=True)
  type = models.CharField(max_length=10, choices=LEASES_TYPES)
  user_score = models.IntegerField()
  full_product_price = models.PositiveBigIntegerField()
  initial_fee = models.PositiveBigIntegerField()
  monthly_fee = models.PositiveBigIntegerField()
  fees_number = models.IntegerField()
  weekly_income = models.IntegerField()
  lease_reason = models.CharField(max_length=100)
  # Fields as @properties
  # next_payment_date = models.DateTimeField(null=True)
  # total_payed = models.PositiveBigIntegerField()
  # last_payment_date = models.DateTimeField(null=True)
  # next_price_installment = models.PositiveBigIntegerField()
  # number_of_delays = models.IntegerField()
  # is_delayed = models.BooleanField()
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leases_users')
  product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='leases_products')
  address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='leases_address')
  rider = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leases_riders', null=True)
  loan_grantor = models.ForeignKey(LoanGrantor, on_delete=models.CASCADE, related_name='leases_loan_grantors')

  @property
  def total_payed(self):
    # sum all payment in status PAYED
    return self.payments.filter(status=PAYMENTS_STATUS.PAID.value).aggregate(models.Sum('amount'))['amount__sum'] or 0
  
  @property
  def payment_date_initial(self):
    # sorted by date
    payments = self.payments.all().order_by('created_at')
    current_sum = 0
    current_date = None
    for payment in payments:
      current_sum += payment.amount
      if current_sum >= self.initial_fee:
        current_date = payment.date
        break
    return current_date
  
  @property
  def next_payment_date(self):
    # TODO: This function should take into account the number of delays    
    initial_fee_date = self.payment_date_initial    
    total_payed = self.total_payed
    if initial_fee_date==None:
      return datetime.datetime.now()
    number_of_fees_payed = (total_payed-self.initial_fee) // self.monthly_fee
    days_between_fees = 7
    return initial_fee_date + datetime.timedelta(days=days_between_fees * number_of_fees_payed)
  
  @property
  def is_delayed(self):
    return self.next_payment_date < datetime.now()

class UserDocumentsLease(models.Model):
  user_document = models.ForeignKey(UserDocument, on_delete=models.CASCADE, related_name='documents_leases_user_documents')
  lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='documents_leases_leases')

  class Meta:
    unique_together = ('user_document', 'lease')

class PaymentDelay(models.Model):
  id = models.AutoField(primary_key=True)
  created_at = models.DateTimeField()
  fee_number = models.PositiveBigIntegerField()
  lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='payment_delays_leases')