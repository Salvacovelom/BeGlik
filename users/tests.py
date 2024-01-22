from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

class TestCustomer(TestCase):
  user_data = {
    "name": "John Doe",
    "email": "johndoe@example.com",
    "username": "johndoe",
    "password": "johndoe",
    "CI": "V-12345678",
  }

  # Before each test, login the admin user
  def setUp(self):
    client = APIClient()    
    response = client.post("/api/user/create-customer", data=self.user_data, format="json")
    self.assertEqual(response.status_code, 201)
    response = client.post("/api/auth/login", data={"username": "johndoe", "password": "johndoe"}, format="json")
    token = response.data["data"]["token"]
    self.header = {"HTTP_AUTHORIZATION": f"Token {token}"}

  def test_create_customer_address(self):
    client = APIClient()
    address_data = {
      "name": "John Doe home",
      "address": "Calle 123, Caracas, Venezuela",
      "latitude": "10.123456",
      "longitude": "-66.123456",
      "description": "Home",
    }
    response = client.post(f"/api/user/address", data=address_data, format="json", **self.header)
    self.assertEqual(response.status_code, 201)
  
  def test_create_customer_company(self):
    client = APIClient()

    company_data = {
      "company": {
        "name": "Company name",
        "web_page": "https://www.company.com",
        "instagram": "@company",
        "facebook": "@company",
        "address": "Company address"
      },
      "seniority_months": 12,
      "position": "CEO",
      "boss": {
        "name": "Boss name",
        "phone_number": "1234567890",
        "email": "boss@gamil.com",
        "address": "Boss address",
        "relationship": "Boss"
      },
      "monthly_income": 100000,
      "web_page": "https://www.company.com"      
    }
    response = client.post(f"/api/user/company", data=company_data, format="json", **self.header)
    self.assertEqual(response.status_code, 201)