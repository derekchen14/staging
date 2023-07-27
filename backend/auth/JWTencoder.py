# This file is responsible for signing , encoding , decoding and returning JWTS
import time
from typing import Dict
import os
import jwt
from dotenv import load_dotenv

load_dotenv('./database/.env')  # take environment variables from .env.

JWT_SECRET = os.getenv("secret")
JWT_ALGORITHM = os.getenv("algorithm")


def token_response(token: str):
  return {
        "access_token": token
  }

# function used for signing the JWT string
# called by signup route in webserver.py
def signJWT(user_email: str) -> Dict[str, str]:
  payload = {
        "user_email": user_email,
        "expires": time.time() + 600
  }
  token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

  return token_response(token)


def decodeJWT(token: str) -> dict:
  try:
    decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return decoded_token if decoded_token["expires"] >= time.time() else None
  except:
    return {}
