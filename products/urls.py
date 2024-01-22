# myapp/urls.py
from django.urls import path
from . import views

# TODO: Add tests to the endpoints
# TODO: Add documentation to the endpoints

urlpatterns = [
    path('name/<str:id>', views.ProductView.as_view()),
    path('all', views.ProductAllView.as_view(), name='products'),
    path('image/all', views.ProductImageUploadView.as_view({'post': 'create', 'get': 'list'})),
    path('image/<int:pk>', views.ProductImageUploadView.as_view({'get': 'retrieve', 'delete': 'destroy', 'patch': 'partial_update'})),
    path('category/<int:id>', views.CategoryView.as_view()), 
    path('category/all', views.CategoryAllView.as_view()), 
]

# public endpoints
# * get all the products
# * get a product by id
# * get all the categories
# * get a category by id

