from django.db import models
from leases.models import Lease
from users.models import User

class Payment(models.Model):
  id = models.AutoField(primary_key=True)
  amount = models.PositiveBigIntegerField()
  created_at = models.DateTimeField(auto_now_add=True)
  date = models.DateTimeField()
  type = models.CharField(max_length=50)
  status = models.CharField(max_length=50)
  currency = models.CharField(max_length=10)
  exchange_rate = models.BigIntegerField()
  lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='payments')
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')