# myapp/urls.py
from django.urls import path
from . import views

# TODO: Add tests to the endpoints
# TODO: Add documentation to the endpoints

urlpatterns = [
    path('<int:id>', views.LeaseView.as_view()),
    path('all', views.LeaseAllView.as_view(), name='leases'),
    path('user/<int:id>', views.UserLeasesView.as_view()),
    path('user/all', views.UserLeasesAllView.as_view()),
    path('<int:id>/status', views.LeaseStatusView.as_view()),
    path('loan-grantor/<int:pk>', views.LoanGrantorView.as_view({'get': 'retrieve'})),
    path('loan-grantor/all', views.LoanGrantorView.as_view({'post': 'create'})),
    path('loan-grantor/company/<int:pk>', views.LoanGrantorCompanyView.as_view({'get': 'retrieve'})),
]