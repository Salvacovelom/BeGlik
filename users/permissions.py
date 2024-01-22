from rest_framework.permissions import BasePermission

class UserViewPermission(BasePermission):
  def has_permission(self, request, view):
    if request.method == 'GET':      
      user_id = view.kwargs['id']
      return request.user.has_perm('user.view_user') or request.user.id == user_id
    if request.method == 'PATCH':
      user_id = view.kwargs['id']
      return request.user.has_perm('user.change_user') or request.user.id == user_id
    if request.method == 'DELETE':
      user_id = view.kwargs['id']
      return request.user.has_perm('user.delete_user') or request.user.id == user_id
    if request.method == 'POST':
      return request.user.has_perm('user.add_user')
    return False

class UserAllViewPermission(BasePermission):
  def has_permission(self, request, view):
    if request.method == 'GET':
      return request.user.has_perm('user.view_user')
    if request.method == 'POST':
      return request.user.has_perm('user.add_user')    
    return False

class GroupViewPermission(BasePermission):
  def has_permission(self, request, view):
    if request.method == 'GET':
      return request.user.has_perm('user.view_group')
    if request.method == 'PATCH':
      return request.user.has_perm('user.change_group')
    if request.method == 'DELETE':
      return request.user.has_perm('user.delete_group')
    if request.method == 'POST':
      return request.user.has_perm('user.add_group')
    return False
