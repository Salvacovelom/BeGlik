from leases.models import Lease
from exceptions.custom_exception import CustomException
from glik.constants import LEASES_STATUS

valid_status = [ status.value for status in LEASES_STATUS ]

def update_lease_status( new_status, lease_id ):
  """ Update the status of a lease. """

  if new_status not in valid_status:
    raise CustomException(message="Invalid status", status_code=400)

  lease = Lease.objects.filter(id=lease_id).first()
  if lease is None:
    raise CustomException(message="Lease not found", status_code=404)
  
  lease.status = LEASES_STATUS[new_status].value
  lease.save()