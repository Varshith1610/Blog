from django.db import models
from django.contrib.auth.hashers import make_password,check_password
import base64
from django.utils.timezone import now
from datetime import datetime
# Create your models here.
class User(models.Model):
    user_id=models.AutoField(primary_key=True)
    username=models.CharField(max_length=20,unique=True)
    password=models.CharField(max_length=1000)
    firstname=models.CharField(max_length=20)
    lastname=models.CharField(max_length=20)
    email=models.EmailField()
    def __str__(self):
        return self.username
    def set_password(self,raw_password):
        self.password=make_password(raw_password)
    def check_password(self,raw_password):
        return check_password(raw_password,self.password)
class Tags(models.Model):
    tags_id=models.AutoField(primary_key=True)
    tag_name=models.CharField(max_length=20)

class Blog(models.Model):
    blog_id=models.AutoField(primary_key=True)
    title=models.CharField(max_length=30)
    user=models.ForeignKey(User,related_name='users',on_delete=models.SET_NULL,null=True)
    blogcontent=models.TextField()
    published_date=models.DateTimeField(auto_now_add=True)
    last_date=models.DateTimeField(auto_now=True)
    likes=models.ManyToManyField(User,related_name="bloglikes",blank=True)
    tags=models.ManyToManyField(Tags,blank=True)
    istemp=models.BooleanField(default=False)
    def __str__(self):
        return self.title
class Comment(models.Model):
    comment_id=models.AutoField(primary_key=True)
    comment=models.TextField()
    sub_comment=models.ForeignKey("self",null=True,blank=True,on_delete=models.CASCADE,related_name="comments")
    likes=models.ManyToManyField(User,related_name="like",blank=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    blog_id=models.ForeignKey(Blog,on_delete=models.CASCADE)
    commented_date=models.DateTimeField(auto_now_add=True)
    updated_date=models.DateTimeField(auto_now=True)
    super_comment=models.ForeignKey("self",null=True,blank=True,on_delete=models.CASCADE,related_name="super_comments")
class BlogMedia(models.Model):
    media_id=models.AutoField(primary_key=True)
    name=models.TextField()
    blog=models.ForeignKey(Blog,on_delete=models.CASCADE)
    media=models.BinaryField()
class CodeBlock(models.Model):
    code_id=models.AutoField(primary_key=True)
    blog=models.ForeignKey(Blog,on_delete=models.CASCADE)
    language=models.CharField(max_length=20,default="")
    python_code=models.TextField(default="")
    javaScript_code=models.TextField(default="")