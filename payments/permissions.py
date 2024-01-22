from rest_framework.permissions import BasePermission

class PaymentViewPermission(BasePermission):
  def has_permission(self, request, view):
    if request.method == 'GET':      
      return request.user.has_perm('payment.view_payment')
    if request.method == 'PATCH':
      return request.user.has_perm('payment.change_payment')
    if request.method == 'DELETE':
      return request.user.has_perm('payment.delete_payment')
    if request.method == 'POST':
      return request.user.has_perm('payment.add_payment')
    if request.method == 'PUT':
      return request.user.has_perm('payment.change_payment')
    return False