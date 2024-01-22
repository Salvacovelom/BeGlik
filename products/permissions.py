from rest_framework.permissions import BasePermission

class ProductViewPermission(BasePermission):
  def has_permission(self, request, view):
    if request.method == 'GET':      
      return True
      # return request.user.has_perm('product.view_product')
    if request.method == 'PATCH':
      return request.user.has_perm('product.change_product')
    if request.method == 'DELETE':
      return request.user.has_perm('product.delete_product')
    if request.method == 'POST':
      return request.user.has_perm('product.add_product')
    return False

class CategoryViewPermission(BasePermission):
  def has_permission(self, request, view):
    if request.method == 'GET':      
      return True
      # return request.user.has_perm('category.view_category')
    if request.method == 'PATCH':
      return request.user.has_perm('category.change_category')
    if request.method == 'DELETE':
      return request.user.has_perm('category.delete_category')
    if request.method == 'POST':
      return request.user.has_perm('category.add_category')
    return False
