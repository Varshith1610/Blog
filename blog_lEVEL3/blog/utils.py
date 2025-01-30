import jwt
import datetime as d
from django.conf import settings
from .models import *
JWT_SECRET=settings.SECRET_KEY
JWT_ALGORITHM ='HS256'
def generate_jwt(user):
    access_payload={
        'user_id':user.user_id,
        'username':user.username,
        'exp':d.datetime.now(tz=d.timezone.utc)+d.timedelta(days=1),
        'iat':d.datetime.now(tz=d.timezone.utc),
    }
    refresh_payload={
        'user_id':user.user_id,
        'username':user.username,
        "email":user.email,
        'exp':d.datetime.now(tz=d.timezone.utc)+d.timedelta(days=7),
        'iat':d.datetime.now(tz=d.timezone.utc),
    }
    access_token=jwt.encode(access_payload,JWT_SECRET,algorithm=JWT_ALGORITHM)
    refresh_token=jwt.encode(refresh_payload,JWT_SECRET,algorithm=JWT_ALGORITHM)
    return access_token,refresh_token

    
def decode_jwt(token):
    try:
        payload=jwt.decode(token,JWT_SECRET,algorithms=[JWT_ALGORITHM])
        print(payload)
        return payload
    except jwt.ExpiredSignatureError:
        return None 
    except jwt.InvalidTokenError:
        return None 

def username(user_id):
    data=User.objects.filter(user_id=user_id)
    return data[0].username

def checking(user,likes):
    return user in likes