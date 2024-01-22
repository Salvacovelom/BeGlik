from payments.models import Payment
from glik.constants import PAYMENTS_STATUS
from exceptions.custom_exception import CustomException

payment_status = [ status.value for status in PAYMENTS_STATUS ]

def update_payment_status(new_status, payment_id):
  """ Update the status of a payment. """
  if new_status not in payment_status:
    raise CustomException(message="Invalid status", status_code=400)
  
  payment = Payment.objects.filter(id=payment_id).first()
  if payment is None:
    raise CustomException(message="Payment not found", status_code=404)

  payment.status = PAYMENTS_STATUS[new_status].value
  payment.save()
