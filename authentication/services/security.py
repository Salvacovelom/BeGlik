'''
In this file we have a service that will be used to
encrypt and decrypt text
'''

import hashlib
# To get the environment variable
import os
from dotenv import load_dotenv
load_dotenv()

class Security_service:
  def __init__(self):
    self.key = os.environ.get("SHA256_SECRET").encode('utf-8')
  
  def encrypt(self, text):
    """Encrypts text using SHA256 and a secret key."""
    encoded_text = text.encode('utf-8')
    digest = hashlib.sha256(encoded_text + self.key).hexdigest()
    return digest

  def decrypt(self,digest):
    """Decrypts text using SHA256 and a secret key."""
    encoded_digest = digest.encode('utf-8')
    decoded_digest = hashlib.sha256(encoded_digest + self.key).hexdigest()
    return decoded_digest


