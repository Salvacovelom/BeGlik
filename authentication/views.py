from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.response import Response
from authentication.models import User
from rest_framework.authtoken.models import Token
from utils.api_response import get_successful_response, get_failed_response
from rest_framework.authtoken.views import ObtainAuthToken
from authentication.services.security import Security_service
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext as _
from notifications.services.email import send_forgot_password_email
import secrets

class LogoutView(APIView):
  permission_classes = [IsAuthenticated]

  def post(self, request):
    request.user.auth_token.delete()
    return get_successful_response(message=_("Logout successful"))

class ForgotPasswordView(APIView):
  def patch(self, request):
    '''
    In this method, we update the user password with the new password, 
    if the token is valid
    '''
    try:
      # Get token and new password from request
      token = request.data['token']
      new_password = request.data['new_password']
      security_service = Security_service()
      new_password = security_service.encrypt(new_password)
    except:
      return get_failed_response(message=_("Token and new password are required"))

    # Update user password 
    user = User.objects.get(forgot_password_token=token)
    user.set_password(new_password)
    user.save()
    
    return get_successful_response(message=_("Change of password successful"))

  def post(self, request):
    '''
    In this method, we create and set the forgot_password_token to the user
    and send an email with the token
    '''

    # Get email from request
    try:      
      email = request.data['email']
    except:
      return get_failed_response(message=_("Email is required"))

    # Get user
    try:
      user = User.objects.get(email=email)
    except:
      # If user does not exist, return success
      return get_successful_response(message=_("The email was sent successfully"))

    # TODO: make a transaction with the following steps

    # Update user forgot_password_token
    # TODO: Generate token service
    token = secrets.token_hex(16)
    user.forgot_password_token = token
    user.save()

    # Send email with token
    # TODO: Send email service
    try:
      send_forgot_password_email( token, user.email )
    except:
      return get_failed_response(message=_("Error sending email"))

    return get_successful_response(message=_("The email was sent successfully"))

class LoginView(ObtainAuthToken):
  def post(self, request, *args, **kwargs):
    print(request.data['password'])
    security_service = Security_service()
    print(request.data['password'])
    request.data['password'] = security_service.encrypt(request.data['password'])
    print(request.data['password'])

    serializer = self.serializer_class(data=request.data, context={'request': request})
    print(request)
    serializer.is_valid(raise_exception=True)
    print(request.data['password'])
    user = serializer.validated_data['user']
    print(request.data['password'])
    token, created = Token.objects.get_or_create(user=user)
    print(request.data['password'])
    return get_successful_response(data={'token': token.key}, message="Login successful")