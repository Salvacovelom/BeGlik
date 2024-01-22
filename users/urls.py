# myapp/urls.py
from django.urls import path
from . import views

# TODO: Add tests to the endpoints
# TODO: Add documentation to the endpoints

urlpatterns = [    
    path('<int:id>', views.UserView.as_view()),    
    path('all', views.UserAllView.as_view()),    
    path('self', views.SelfUserView.as_view()),
    path('company', views.UserCompanyView.as_view()),
    path('address/<int:id>', views.UserAddressView.as_view()),
    path('address/all', views.UserAddressAllView.as_view()),
    path('document/<int:id>', views.UserDocumentView.as_view()),
    path('document/all', views.UserDocumentAllView.as_view()),    
    path('group', views.GroupView.as_view()),
]

# public endpoint
urlpatterns += [
    path('create-customer', views.CustomerUserView.as_view()),
]