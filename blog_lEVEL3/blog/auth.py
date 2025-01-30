from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header
from .models import *
from .utils import *
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

def jwt_requried(view_func):
    def wrapper(request,*args,**kwargs):
        auth_header=request.headers.get('Authorization')
        
        if not auth_header:
            return JsonResponse({'error':"authorization header requried"},status=401)
        try:
            token=auth_header.split(' ')[1]
            # print(token)
            payload=jwt.decode(token,JWT_SECRET,algorithms=[JWT_ALGORITHM])
            user=User.objects.get(user_id=payload['user_id'])
            # print(user)
            request.user=user
        except (jwt.ExpiredSignatureError,jwt.InvalidTokenError):
            return JsonResponse({'error':"Invliad or expired"},status=401)
        except User.DoesNotExist:
            return JsonResponse({'error':"User not found"})
        return view_func(request,*args,**kwargs)
    return wrapper
   



def getTage(tags_id):
    tags=Tags.objects.filter(tags_id__in=tags_id)
    return [tag.tag_name for tag in tags]


def getUser(user_id):
    data=get_object_or_404(User,user_id=user_id)
    return data.username