from rest_framework import serializers
from .models import *
class Blogserializer(serializers.ModelSerializer):
    class Meta:
        model=Blog
        fields="__all__"
class Codeserializer(serializers.ModelSerializer):
    class Meta:
        model=CodeBlock
        fields="__all__"
class comment_serializer(serializers.ModelSerializer):
    class Meta:
        model=Comment
        fields="__all__"
class tags_serializer(serializers.ModelSerializer):
    class Meta:
        model=Tags
        fields="__all__"    
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields="__all__"  
class MediaSerializer(serializers.ModelSerializer):
    class Meta:
        model=BlogMedia
        fields="__all__"   