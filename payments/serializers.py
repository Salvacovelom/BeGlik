from rest_framework import serializers
from leases.models import Lease
from payments.models import Payment
from users.models import User

# ===================== #
#  Models Serializers   #
# ===================== #

class PaymentSerializer(serializers.ModelSerializer):
  lease = serializers.PrimaryKeyRelatedField(queryset=Lease.objects.all())
  user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
  class Meta:
    model = Payment
    fields = ('__all__')
  
  # TODO: to report a payment the lease have to be of the user