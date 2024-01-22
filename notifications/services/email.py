from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string, get_template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import os

# ================= #
#  frontend urls    #
# ================= #

FRONT_END_URL = os.environ.get("FRONTEND_BASE_URL")

def get_forgot_password_url(token):
  return FRONT_END_URL + "/forgot-password/" + token

# docs:
# https://docs.djangoproject.com/en/dev/topics/email/

def send_email_to_user( user, subject, message ):
  user_email = user.email
  send_mail( subject, message, settings.DEFAULT_FROM_EMAIL, [user_email], fail_silently=True)

def send_forgot_password_email( token, email ):
  url = get_forgot_password_url(token)
  # Message
  subject = "Recuperar contraseña"
  text = "Recupera tu contraseña en el siguiente link: " + url
  with open("templates/email/forgot_password.html") as f:
    html = f.read()
    msg = EmailMultiAlternatives(
      subject=subject,
      body=text,
      from_email=settings.DEFAULT_FROM_EMAIL,
      to=[email],
    )
    # add context to the template
    html_content = html.replace("{{ url }}", url)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

  print("Email sent to " + email)