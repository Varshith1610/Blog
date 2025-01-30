from django.urls import path
from blog.views import *
urlpatterns=[
    path('signup/',signup_view,name='signup'),
    path('signin/',login_view,name='login'),
    path('refresh',refresh_token_view,name='refresh_token_view'),
    path('uploadmedia/<int:blog_id>/',upload_media,name='upload_media'),
    path('uploadblog/',upload_and_fetch_blog),
    path('addlike/<int:comment_id>',add_like_comment),
    path('addblock/<int:blog_id>',add_block),
    path('addcomment/<int:blog_id>',add_comment),
    path('addsubcomment/<int:comment_id>/<int:blog_id>',add_sub_comment),
    path('getcomments/<int:blog_id>',get_comment),
    path('tags',gettags),
    path('profile',updateuser),
    path('updated/<int:blog_id>',update_blog),
    path('getblog/<int:blog_id>',getblog),
    path('tempdelete/<int:blog_id>',tempdeleteblog),
    path('getusers',getuser),
    path('republish/<int:blog_id>',republishblog),
    path('addcomment/<int:blog_id>',add_comment),
    path('like/<int:blog_id>',addlike),
    path('edit/<int:comment_id>',edit_comment),
    path('delete/<int:comment_id>',deleteComment),
    path('uploadmedia/<int:blog_id>',upload_media),
    path('getmedia/<int:blog_id>',blog_files,name='blog_files'),
    path('getonemedia/<int:media_id>',getmedia,name='getmedia'),
    path('getcode/<int:blog_id>',get_code_block),
    path('getCode/<int:blog_id>',get_codeBlock)


 ]