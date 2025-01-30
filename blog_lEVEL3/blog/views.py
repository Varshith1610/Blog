from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from .models import *
from .utils import *
from .auth import *
import mimetypes
from .serializer import *
from django.core.paginator import Paginator
from django.contrib.auth.hashers import make_password
from django.db.models import Count
# import pytz
# from django.db import transaction
from django.http import HttpResponse
import json
"""creating new account"""
@csrf_exempt
@api_view(['POST'])
def signup_view(request):
    email=request.data.get('email')
    username=request.data.get('username')
    password=request.data.get('password')
    firstname=request.data.get('firstname')
    lastname=request.data.get('lastname')
    
    if not email or not username or not password:
        return JsonResponse({'error':'fill all the fleids'},
                            status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(email=email).exists():
        return JsonResponse({'error':"already used this email"},
                                status=status.HTTP_400_BAD_REQUEST)

    if User.objects.filter(username=username).exists():
        return JsonResponse({'error':"already used this username"},
                            status=status.HTTP_400_BAD_REQUEST)
    
    user=User(email=email,username=username,firstname=firstname,lastname=lastname)
    user.set_password(password)
    user.save()
    return JsonResponse({"message":"user created successfully"},
                        status=status.HTTP_201_CREATED)

"""login to access the blog"""
@csrf_exempt
@api_view(['POST'])
def login_view(request):
    username=request.data.get('username')
    password=request.data.get('password')
    print(password)
    print(username)
    if not username and not password:
        return JsonResponse({'error':'username and password are requried to login in'},
                            status=status.HTTP_400_BAD_REQUEST)    
    

    try:
        user=User.objects.get(username=username)
    
    except User.DoesNotExist:
        return JsonResponse({'error':"account doesnot exists , create a account"},
                            status=status.HTTP_400_BAD_REQUEST)
    if not user.check_password(password):
        print(user.check_password(password))
        return JsonResponse({'error':'Invalid login creadtials'},
                            status=status.HTTP_400_BAD_REQUEST)

    access_token,refresh_token=generate_jwt(user) 
    return JsonResponse({
        'access_token':access_token,
        'refresh_token':refresh_token},status=status.HTTP_200_OK)
    
"""posting refresh token"""
@csrf_exempt
@api_view(['POST'])
def refresh_token_view(request):
    refresh_token=request.data.get('refresh_token')
    print(refresh_token)
    if not refresh_token:
        return JsonResponse({'error':'refresh token is requried'},
                            status=status.HTTP_400_BAD_REQUEST)
    payload=decode_jwt(refresh_token)
    print(payload)
    
    if not payload:
        return JsonResponse({'error':"Invalid token or expired refresh token"},
                            status=status.HTTP_400_BAD_REQUEST)
    try:

        user=User.objects.get(user_id=payload['user_id'])

    except User.DoesNotExist:
        return JsonResponse({'error':"user not found"},
                            status=status.HTTP_404_NOT_FOUND)

    access_token,_=generate_jwt(user)
    return JsonResponse({
                          'access_token':access_token}
                          ,status=status.HTTP_200_OK)



@api_view(['POST','GET'])
@jwt_requried
def upload_and_fetch_blog(request):
    """ 
    Params : request 
    Returns : Posting a blog and Retriving all Blogs
    """
    if request.method=='POST':
        media=request.data.getlist('files')
        new=upload_and_fetch_blog(request.data,request.user_id)
        serializer=Blogserializer(data=new)
        print("kkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkkk")
        print(media,new)
        if serializer.is_valid():
            serializer.save()
            upload_media(media_files,serializer.data['blog_id'])
            return Response(serializer.data,    
                            status=status.HTTP_201_CREATED)

        return Response(serializer.errors,  
                        status.HTTP_400_BAD_REQUEST)

    if request.method=='GET':
        tag_id=request.GET.get('tags','')   

        if tag_id:
            tag_list=tag_id.split(',')
            blogs=Blog.objects.filter(tags__tags_id__in=tag_list)
            page_number=request.GET.get('page',1)
            blogs_per_page=request.GET.get('blogs',7)
            paginator=Paginator(blogs,blogs_per_page)

            try:
                page=paginator.page(page_number)

            except:
                page=paginator.page(1)
            page_object_serialzer=Blogserializer(page,many=True)
            for data in page_object_serialzer.data:
                
                data['user']=getUser(data['user'])
                data['tags']=getTage(data['tags'])  
            return Response({
                'blog':page_object_serialzer.data,
                'has_next':page.has_next(),
                'next_page_number':page.next_page_number() if page.has_next()else None,
            })

        blogs=Blog.objects.all().order_by('-published_date')
        page_number=request.GET.get('page',1)
        blog_per_page=request.GET.get('blogs',7)
        sortby=request.GET.get('sortby',"new")
        myblog=request.GET.get('myblog',"false")
        user=request.GET.get('user','all')
        istemp=request.GET.get('istemp',"false")
        if user=='all':
            blogs=Blog.objects.all().order_by('-published_date').filter(istemp=False)
            print("12345")
           
        if user=='me':
            print(request.user.user_id)
            users=User.objects.get(user_id=request.user.user_id)
            blogs=Blog.objects.filter(user=users).filter(istemp=False).order_by('-published_date')
            print(blogs)
        if istemp=="true":
            print('po')
            blogs=Blog.objects.filter(user=request.user.user_id).filter(istemp=True)
            print(blogs)

        if sortby=='likes':
            blogs=blogs.annotate(likes_count=Count('likes')).order_by('-likes_count')
   
        paginator=Paginator(blogs,blog_per_page)
        try:
            page_obj=paginator.page(page_number)

        except:
            page_obj=paginator.page(1)
        page_object_serialzer=Blogserializer(page_obj,many=True)
        for data in page_object_serialzer.data:
            user=User.objects.get(user_id=data['user']).username
            comment_blog=Blog.objects.get(blog_id=data['blog_id'])
            comments=Comment.objects.filter(blog_id=comment_blog)
            data['likes_count']=len(data['likes'])
            data['user']=getUser(data['user'])
            data['tags']=getTage(data['tags'])
            data['comment_count']=len(comments)
            # data['liked']=data['likes']
            
        
        return Response({
            'blogs':page_object_serialzer.data,
            'has_next':page_obj.has_next(),
            'next_page_number':page_obj.next_page_number() if page_obj.has_next()else None,
            'request':request.user.user_id,
            
        })



@api_view(['PATCH'])
@jwt_requried
def edit_comment(request,comment_id):

    """ 
    Params : request and Comment_id
    Returns : Edited Comment data
    """
    comment_data=Comment.objects.get(comment_id=comment_id)
    data=request.data
    user=request.user
    print(request.data)
    edited_comment={
        "comment":data['comment_data']
    }
    serializer=comment_serializer(comment_data,data=edited_comment,partial=True)
    if serializer.is_valid():
        serializer.save()
    else:
        return JsonResponse("error")
    return JsonResponse(serializer.data)


"""uploading medias to a blog"""
@api_view(['POST'])
@jwt_requried
def upload_media(request,blog_id):

    """ 
    Params : request and blog_id
    Returns :uploaded media with blog_id and binary data
    """
    print("iiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
    try:
        blog=Blog.objects.get(blog_id=blog_id)
    except Blog.DoesNotExist:
        return JsonResponse({'error':"blog does not exists"},
                            status=status.HTTP_400_BAD_REQUEST)
    files=request.FILES.getlist('files')
    if not files:
        return JsonResponse({'error':"no files are uploaded"},
                            status=status.HTTP_400_BAD_REQUEST)

    max_file_size=10*1024*1024
    uploaded_files=[]
    
    for file in files:
        if file.size>max_file_size:
            return JsonResponse({'error':"max_length execeded"})
        file_content=file.read()
        media_instance=BlogMedia.objects.get_or_create(blog=blog,name=file.name,media=file_content)
        uploaded_files.append(media_instance)
    return JsonResponse({"message":"files uploaded"})
    # for file in files:
    #     print(file)
    #     if file.size>10*1024*1024:
    #         return JsonResponse({'error':'size is greater'},
    #                                 status=status.HTTP_400_BAD_REQUEST)

    #     file_content=file.read()
        
    #     BlogMedia.objects.create(name=file.name,media=file_content,blog=blog)
    # return JsonResponse({'message':"files uploaded"})
from django.urls import reverse
@api_view(['GET'])
@jwt_requried
def blog_files(request,blog_id):
    blog_media=BlogMedia.objects.filter(blog=blog_id)
    # files=[
    #     {'id':media.media_id,
    #      'url':request.build_absolute_uri(reverse('getmedia',args=[media.media_id]))}
    #     for media in blog_media
    

    # ]
 

    # return JsonResponse({"blog_id":blog_id,"files":files},safe=False)
    allmedia=[]
    for media in blog_media:
        image_data=media
        allmedia.append(image_data.name)
    return JsonResponse({"media":allmedia})


@api_view(['GET'])
@jwt_requried
def getmedia(request,blog_id):
    media=BlogMedia.objects.filter(blog=blog_id)
    serializer=MediaSerializer(media,many=True)
    return Response({"media":serializer.data})


@api_view(['POST'])
@jwt_requried
def addlike_comment(request,comment_id):
    """ 
    Params : request and comment_id
    Returns : addlike to comment through comment_id
    """
    comment_data=Comment.objects.get(comment_id=comment_id)
    comment_data.likes.add(request.user)
    return JsonResponse(comment_data.likes.count(),safe=False)



@api_view(['POST'])
@jwt_requried
def add_block(request,blog_id):

    """ 
    Params : request and blog_id
    Returns : adds blocks to the blog_id
    """
    blog=Blog.objects.filter(blog_id=blog_id)
    blog=blog[0]
    Block_data={
        "blog":blog_id, 
        "python_code":request.data["python_code"],
        "javaScript_code":request.data['javascript_code']

    }
    block_serializer=Codeserializer(data=Block_data)
    if blog.user!=request.user: 
        return JsonResponse({"message":"Bad Request"},
                             status=status.HTTP_400_BAD_REQUEST)
    if block_serializer.is_valid():
        block_serializer.save()
        return JsonResponse({'message':"Block of code  Posted"},
                              status=status.HTTP_200_OK)

    return JsonResponse({"message":"Bad Request"},
                         status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
@jwt_requried
def get_code_block(request,blog_id):
    code=CodeBlock.objects.filter(blog_id=blog_id)
    serializer=Codeserializer(code,many=True)
    return JsonResponse({"code":serializer.data})

@api_view(['GET'])
@jwt_requried
def get_codeBlock(request,blog_id):
    print("ppppppppppppp")
    code=CodeBlock.objects.filter(blog_id=blog_id)
    language=request.GET.get('language','python')
    print(language)
    result=[]
    for codes in code:
        if language=='python':
            print("oiuhi")
            codeblock=codes.python_code
            lang=codes.language
            print(codeblock)
        if language=='javaScript':
            codeblock=codes.javaScript_code
            lang=codes.language
        
        result.append({'code':codeblock,'language':lang})
        
    return JsonResponse(result,safe=False)

@api_view(['POST'])
@jwt_requried
def add_comment(request,blog_id):
    """ 
    Params : request and blog_id
    Returns : comment is added to blog_id
    """
    comment_data={
        "comment":request.data["comment"],
        "user":request.user.user_id,
        "blog_id":blog_id
    }
    comment=comment_serializer(data=comment_data)
    print(comment)
    if comment.is_valid():
        comment.save()
        return JsonResponse({'message':"Comment is added to the blog "}
                            ,status=status.HTTP_200_OK)

    return JsonResponse({"message":comment.errors})


@api_view(['POST'])
@jwt_requried
def add_sub_comment(request,blog_id,comment_id):
    """ 
    Params : request , blog_id and comment_id
    Returns : adds to subcomment to a comment
    """
    print(comment_id)
    print(request.data['comment'])
    sub_comment_data={
        "user":request.user.user_id,
        'comment':request.data['comment'],
        'blog_id':blog_id,
        'super_comment':comment_id
    }
    comments_serializer=comment_serializer(data=sub_comment_data)

    if comments_serializer.is_valid():
        
        comments_serializer.save()
        return JsonResponse({'message':"Comment added to the comment"}
                            ,status=status.HTTP_200_OK)
    print(comments_serializer.data) 
    return JsonResponse({'message':"Bad REquest"},
                         status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@jwt_requried
def add_like_comment(request,comment_id):
    """ 
    Params : request  and comment_id
    Returns : adds like to comment_id
    """
    comment_data=Comment.objects.get(comment_id=comment_id)
    if request.user in comment_data.likes.all():
        comment_data.likes.remove(request.user)
        liked=False
    else:
        comment_data.likes.add(request.user)
        liked=True
    return JsonResponse({'liked':liked,'totallikes':comment_data.likes.count()})


@api_view(['POST'])
@jwt_requried
def addlike(request,blog_id):
    """ 
    Params : request and blog_id
    Returns :adds like to blog_id
    """
    blog=Blog.objects.get(blog_id=blog_id)
    if request.user in blog.likes.all():
        blog.likes.remove(request.user)
        liked=False
    else:
        blog.likes.add(request.user)
        liked=True
    return JsonResponse({'liked':liked,'total_likes':blog.likes.count()})


@api_view(['GET'])
@jwt_requried
def get_comment(request,blog_id):
    """ 
    Params : request and blog_id
    Returns : Retrives comments of blog_id with LazingLoading
    """
    super_comment=request.GET.get('super_comment',0)
    comments_data=Comment.objects.filter(blog_id=blog_id).filter(super_comment=None).order_by('-commented_date')
    print(super_comment)
    if super_comment!='':
        comments_data=Comment.objects.filter(super_comment=super_comment)
        # comment_data=comment.comment_set.all()  
    page_number=request.GET.get('page',1)
    comment_per_page=request.GET.get('comments',2)
    enter=request.user.user_id
    paginator_data=Paginator(comments_data,comment_per_page)
    try:
        page_obj=paginator_data.page(page_number)
    except:
        page_obj=paginator_data.page(1)
    serializer=comment_serializer(page_obj,many=True)
    for comment in serializer.data:
        comment['user']=username(comment['user'])
        comment['likes_count']=len(comment['likes'])
        comment['is_liked']=checking(request.user.user_id,comment['likes'])
        comment['editable']=username(request.user.user_id)
        print(serializer.data)
        comment['sub']=len(Comment.objects.filter(super_comment=comment['comment_id']))
    return Response({
        'comments':serializer.data,
        'has_next':page_obj.has_next(),
        'next_page_number':page_obj.next_page_number() if page_obj.has_next() else None,
    })


@api_view(['GET','POST'])
@jwt_requried
def gettags(request):
    """ 
    Params : request 
    Returns : Retrives every tags in the database and creates new tag and also creating a blog
    """
    if request.method=='GET':
        tags=Tags.objects.all()
        serializer=tags_serializer(tags,many=True)
        print(serializer.data)
        return Response({"tags":serializer.data})
    if request.method=='POST':
        print(request.data)             
        blog={
        "title":request.data['title'],
        "blogcontent":request.data['blogcontent'],
        "user":request.user.user_id,
        "tags":request.data.getlist('tags'),
       }
        # code_title=request.data['language']
        # python_block=request.data['python_block']
        # javascript_block=request.data['javascript_block']
        newTags=request.data.getlist('newtags')
        Blogs=Blogserializer(data=blog)
        if Blogs.is_valid():
           print("hello")
           Blogs.save()
           
           created_blog=Blog.objects.get(blog_id=Blogs.data['blog_id'])
        #    print(created_blog+"jwnjkc")
        else:
            print("error",Blogs.errors)
        for addcode in request.data.getlist('code'):
            try:
                addcode=json.loads(addcode)
                print(addcode)
                CodeBlock.objects.create(language=addcode['language'],javaScript_code=addcode['javascript_code'],python_code=addcode['python_code'],blog=created_blog)
            except json.JSONDecodeError as e:
                print("invalid",addcode,e)
        
        for tag in newTags:
            print("tag",tag)
            nTag=Tags.objects.create(tag_name=tag)
            # print(nTag)
            created_blog.tags.add(nTag.tags_id) 
        
        for file in request.FILES.getlist("media_files"):
            BlogMedia.objects.create(
                blog=created_blog,
                name=file.name,
                media=file.read()
            )
        else:
            print(Blogs.errors)
        return Response(Blogs.data)


@api_view(['PATCH','GET'])
@jwt_requried
def updateuser(request):
    """ 
    Params : request 
    Returns : updating the user details and retriving user details
    """
    if request.method=='GET':
        user=request.user.user_id
        user_details=User.objects.get(user_id=user)
        user_serializer=UserSerializer(user_details)
        return Response({
            'details':user_serializer.data
        })
    if request.method=='PATCH':
        data = request.data
        data.pop('confirmpassword')
        print(data)
        if data['password']=='':
            data.pop('password')
        else:
            data['password']=make_password(data['password'])
        user_details=User.objects.get(user_id=request.user.user_id)
        user_serializer=UserSerializer(user_details,data=request.data,partial=True)
        if user_serializer.is_valid():
            user_serializer.save() 
            return Response({
                'details':user_serializer.data
            })

        return Response({
            'message':"update failed"
        },status=400)



@api_view(['PATCH'])
@jwt_requried
def update_blog(request,blog_id):
    """ 
    Params : request and blog_id
    Returns : Patching a blog
    """
    user=request.user.user_id
    data=request.data
   
    nblog=Blog.objects.get(blog_id=blog_id)
    
    blogs={
        "title":request.data['title'],
        "blogcontent":request.data['content'],
        "user":request.user.user_id,
        "tags":request.data.getlist('tags')
    }
    newTags=request.data.getlist('newtags')
    Blogser=Blogserializer(nblog,data=blogs,partial=True)
    if Blogser.is_valid():
        Blogser.save()
    else:
        return Response(Blogser.errors)
    if len(newTags)==0:
        pass
    else:
        for tag in newTags:
            n=tag=Tags.objects.create(tag=tag)
        created_blog.tags.add(nTag.tag_id)
    return Response(Blogser.data)



@api_view(['GET'])
@jwt_requried
def getblog(request,blog_id):
    """ 
    Params : request and blog_id
    Returns : Retriving blog data
    """
    user=request.user.user_id
    blog=Blog.objects.get(blog_id=blog_id)
    serializer=Blogserializer(blog)
    iswriter=False
   
    if serializer.data['user']==user:
        iswriter=True

    blogs=Blog.objects.get(blog_id=serializer.data['blog_id'])
    author=User.objects.get(user_id=serializer.data['user'])
    data=serializer.data.copy()
    data['user']=user
    data['likes']=serializer.data['likes']
    data['likes_count']=len(data['likes'])
    data['is_liked']=checking(request.user.user_id,data['likes'])

    return Response({"blog":data  ,
                    "user": blog.user.username,
                    "iswriter":iswriter,
                     
                     })
    

@api_view(['DELETE'])
@jwt_requried
def tempdeleteblog(request,blog_id):
    """ 
    Params : request and blog_id
    Returns : temporary deleting the blog
    """
    blog=Blog.objects.get(blog_id=blog_id)
    blog.istemp=True
    blog.save()
    return Response("blog deleted")


@api_view(['GET'])
@jwt_requried
def getuser(request):
    user=User.objects.all()
    serializer=UserSerializer(user,many=True)
    return Response({"users":serializer.data})


@api_view(['POST'])
@jwt_requried
def republishblog(request,blog_id):
    """ 
    Params : request and blog_id
    Returns :republishing the temparory delete blog
    """
    print("hhiugfgyfygf")
    blog=Blog.objects.get(blog_id=blog_id)
    print(blog)
    blog.delete()
    print(request.data)
    blogs={
        "title":request.data['title'],
        "blogcontent":request.data['content'],
        "user":request.user.user_id,
        "tags":request.data.getlist('tags')
    }
    print(blogs)
    newTags=request.data.getlist('newtags')
    Blogser=Blogserializer(data=blogs)
    if Blogser.is_valid():
        Blogser.save()
    else:

        return Response(Blogser.errors)
    created_blog=Blog.objects.get(blog_id=Blogser.data['blog_id'])
    if len(newTags)==0:
        pass
    else:
        for tag in newTags:
            n=tag=Tags.objects.create(tag=tag)
        created_blog.tags.add(nTag.tag_id)
    print(Blogser.data)
    return Response(Blogser.data)




@api_view(['POST'])
@jwt_requried
def sub_comment(request,blog_id):
    """ 
    Params : request and blog_id
    Returns :posting comments to blogs
    """

    comment_data={
        "user":request.user.user_id,
        'comment':request.data['comment'],
        'blog_id':blog_id,
        'sub_comment':None
    }

    comments_serializer=comment_serializer(data=sub_comment_data)
    print(comments_serializer.is_valid())
    print(comments_serializer)
    if comments_serializer.is_valid():
        comments_serializer.save()
        return JsonResponse({'message':"Comment added to the comment"}
                            ,status=status.HTTP_200_OK)

    return JsonResponse({'message':"Bad REquest"},
                         status=status.HTTP_400_BAD_REQUEST)





@api_view(['DELETE'])
@jwt_requried
def deleteComment(request,comment_id):
    """ 
    Params : request and comment_id
    Returns : deleting a comment which returns in
              deleting its all subcommnets
    """
    comment=Comment.objects.get(comment_id=comment_id)
    comment.delete()
    return JsonResponse("deleted",safe=False)



# @api_view(['POST'])
# def updated_post_blog(request):
#     try:
#         data=json.loads(request.body)
#         code=data.get('code','')
#         if not code:
#             return JsonResponse({'error':"cannot be error"})
         
#          blog,created=Blog.objects.get_or_create()