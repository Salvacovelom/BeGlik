from typing import Optional
from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from authentication.services.security import Security_service
import django.utils.timezone as timezone
from .managers import SoftDeleteManager
from glik.constants import DOCUMENTS_NEEDED_FOR_PERSONAL_LEASE, DOCUMENTS_NEEDED_FOR_JURIDIC_LEASE, USER_TYPES_OPTIONS, GROUPS

class UserContact(models.Model):
    """
    A users_contact model.

    Attributes:
        id: The primary key of the contact.
        name: The name of the contact.
        phone_number: The contact's phone number.
        relationship: The contact's relationship to the user.
        address: The contact's address.
        email: The contact's email address.
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=50)
    relationship = models.CharField(max_length=50)
    address = models.CharField(max_length=200)
    email = models.CharField(max_length=50)

# ========================= # 
#    Users of the system    #
# ========================= #

# "Substituting a custom User model" in https://docs.djangoproject.com/en/4.2/topics/auth/customizing/#auth-custom-user
class User(AbstractUser):
    # We inherit from AbstractUser the fields: username, first_name, last_name, email, password
    # groups, user_permissions, is_staff, is_active (read description), is_superuser, last_login, and date_joined
    # User identification    
    country_user_id = models.CharField(max_length=10, blank=True, unique=True, help_text="in Venezuela the CI, in spain DNI")
    rif = models.CharField(max_length=10, blank=True, null=True, unique=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    passport_number = models.CharField(max_length=100, null=True)
    nationality = models.CharField(max_length=100, null=True)
    birth_date = models.DateTimeField(null=True)
    type = models.CharField(max_length=10, choices=USER_TYPES_OPTIONS, default='natural')
    # Internal fields of the model
    forgot_password_token = models.CharField(max_length=100, blank=True, null=True, unique=True, help_text="Token to reset password")

    def __str__(self):
        return self.username + " | " + self.get_full_name() 
    
    def set_password(self, raw_password: str ) -> None:
        security_service = Security_service()
        return super().set_password(security_service.encrypt(raw_password))

    # Partial update used in serizalizers 
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self
    
    @property
    def dictionary_of_documents(self):
        documents = {}
        for document in self.documents.all():
            documents[document.name] = document.document.url
        return documents
    
    def validate_document_list( self, documents, DOCUMENT_MATRIX ):
        for document_group in DOCUMENT_MATRIX:
            have_one = False
            for document in document_group:
                if document in documents:
                    have_one = True
                    break
            if not have_one:
                return False, "You need one of the following documents: " + ", ".join(document_group) + "."
        return True, "Documents are valid"
    
    @property
    def is_admin(self):
        return self.groups.filter(name='admin').exists()

    @property
    def is_customer(self):
        return self.groups.filter(name=GROUPS['CUSTOMER']['name']).exists()
    
    @property
    def can_create_leases(self):
       documents = self.dictionary_of_documents       
       if self.type == 'natural':
            # Only customers can create leases
            if not self.is_customer: return False, "User is not a customer"
            # Validate all the documents
            ok, message = self.validate_document_list(documents, DOCUMENTS_NEEDED_FOR_PERSONAL_LEASE)
            if not ok: return False, message
            # Validate all the customer information
            # null_fields = self.customer.null_fields
            # if len(null_fields) > 0: return False, "The following fields are required: " + ", ".join(null_fields.keys())
            return True, "Documents are valid"
       elif self.type == 'juridic':
            return self.validate_document_list(documents, DOCUMENTS_NEEDED_FOR_JURIDIC_LEASE)
       else:
            return False, "User type is not valid"
       

class CustomerUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer', null=False)    
    # Extra user information
    birth_place = models.CharField(max_length=200, null=True)
    landline_number = models.CharField(max_length=100, null=True)
    instagram = models.CharField(max_length=100, null=True)
    facebook = models.CharField(max_length=100, null=True)
    twitter = models.CharField(max_length=100, null=True)
    linkedin = models.CharField(max_length=100, null=True)
    contact_user_reference = models.ForeignKey(UserContact, on_delete=models.CASCADE, related_name='references', null=True)
    # Flags 
    have_health_insurance = models.BooleanField(null=True)
    have_islr_declaration = models.BooleanField(null=True)
    have_consignment = models.BooleanField(null=True)
    # Internal fields of the model
    score = models.IntegerField(default=0, help_text="Credit score")

    def __str__(self) -> str:
        return self.user.username + " | " + self.user.get_full_name()

    # Partial update used in serizalizers 
    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        return self
    
    @property
    def null_fields(self):
        errors = {}
        if self.birth_place is None:
            errors['birth_place'] = ["Birth place is required"]
        if self.landline_number is None:
            errors['landline_number'] = ["Landline number is required"]
        if self.instagram is None:
            errors['instagram'] = ["Instagram is required"]
        if self.facebook is None:
            errors['facebook'] = ["Facebook is required"]
        if self.twitter is None:
            errors['twitter'] = ["Twitter is required"]
        if self.linkedin is None:
            errors['linkedin'] = ["Linkedin is required"]
        if self.contact_user_reference is None:
            errors['contact_user_reference'] = ["Contact user reference is required"]
        if self.have_health_insurance is None:
            errors['have_health_insurance'] = ["Have health insurance is required"]
        if self.have_islr_declaration is None:
            errors['have_islr_declaration'] = ["Have islr declaration is required"]
        if self.have_consignment is None:
            errors['have_consignment'] = ["Have consignment is required"]
        return errors

# =============== # 
#  Other models   #
# =============== #

class Company(models.Model):
    """
    A company model.

    Attributes:
        id: The primary key of the company.
        name: The name of the company.
        web_page: The company's web page.
        instagram: The company's Instagram username.
        facebook: The company's Facebook username.
        address: The company's address.
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    web_page = models.TextField()
    instagram = models.CharField(max_length=50)
    facebook = models.CharField(max_length=50)
    address = models.CharField(max_length=200)

    """
    JSON representation of the model.
    {
        "name": "Company name",
        "web_page": "https://www.company.com",
        "instagram": "@company",
        "facebook": "@company",
        "address": "Company address"
    }
    """

class UserCompany(models.Model):
    """
    A users_companies model.

    Attributes:
        company_id: The ID of the company.
        user_id: The ID of the user.
        seniority_months: The user's seniority in months at the company.
        position: The user's position at the company.
        boss_id: The ID of the user's boss.
        monthly_income: The user's monthly income.
        web_page: The company's web page.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users', null=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='companies', null=False)
    seniority_months = models.IntegerField(null=False)
    position = models.CharField(max_length=50, null=False)
    boss = models.ForeignKey(UserContact, on_delete=models.CASCADE, related_name='bosses', null=True)
    monthly_income = models.BigIntegerField(null=False)
    web_page = models.TextField(null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["company_id", "user_id"], name="unique_users_companies"
            ),
        ]

class UserDocument(models.Model):
  id = models.AutoField(primary_key=True)
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents', null=False)
  created_at = models.DateTimeField(auto_now_add=True)
  name = models.CharField(max_length=75)
  is_deleted = models.BooleanField(default=False)    
  document = models.FileField(upload_to='user_documents', null=False)

  objects = models.Manager()
  undeleted_objects = SoftDeleteManager()

  def soft_delete(self):
    self.is_deleted = True
    self.save()

  def restore(self):
    self.is_deleted = False
    self.save()
    
class Address(models.Model):
  id = models.AutoField(primary_key=True)
  name = models.CharField(max_length=50)
  description = models.TextField()
  latitude = models.DecimalField(max_digits=9, decimal_places=6)
  longitude = models.DecimalField(max_digits=9, decimal_places=6)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  created_at = models.DateTimeField(auto_now_add=True)
  is_deleted = models.BooleanField(default=False)    

  objects = models.Manager()
  undeleted_objects = SoftDeleteManager()

  def soft_delete(self):
    self.is_deleted = True
    self.save()

  def restore(self):
    self.is_deleted = False
    self.save()