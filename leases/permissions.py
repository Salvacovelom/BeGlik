from rest_framework.permissions import BasePermission
from leases.models import Lease, LoanGrantor

class LeaseViewPermission(BasePermission):
  def has_permission(self, request, view):
    if request.method == 'GET':     
      lease_id = view.kwargs['id']
      is_his_lease = Lease.objects.get(id=lease_id, user=request.user).exist()
      return request.user.has_perm('lease.view_lease') or is_his_lease
    if request.method == 'PATCH':
      return request.user.has_perm('lease.change_lease')
    if request.method == 'DELETE':
      return request.user.has_perm('lease.delete_lease')
    if request.method == 'POST':
      return request.user.has_perm('lease.add_lease')
    if request.method == 'PUT':
      return request.user.has_perm('lease.change_lease')
    return False

class LeaseAllViewPermission(BasePermission):
  def has_permission(self, request, view):
    if request.method == 'GET':
      return request.user.has_perm('lease.view_lease')
    if request.method == 'POST':
      return True
    return False

class LoanGrantorViewPermission(BasePermission):
  # used also for loan grantor company
  def has_permission(self, request, view):
    if request.method == 'GET':     
      return True
    if request.method == 'PATCH':
      return request.user.has_perm('loan_grantor.change_loan_grantor')
    if request.method == 'DELETE':
      return request.user.has_perm('loan_grantor.delete_loan_grantor')
    if request.method == 'POST':
      return True
    if request.method == 'PUT':
      return request.user.has_perm('loan_grantor.change_loan_grantor')
    return False