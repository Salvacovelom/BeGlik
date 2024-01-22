# myapp/urls.py
from django.urls import path
from . import views

# TODO: Add tests to the endpoints
# TODO: Add documentation to the endpoints

urlpatterns = [
    # path('<int:id>', views.PaymentView.as_view()),
    path('all', views.PaymentAllView.as_view(), name='payments'),
    path('lease/<int:id>', views.LeasePaymentView.as_view()),
    path('<int:id>/status', views.PaymentStatusView.as_view()),
]

