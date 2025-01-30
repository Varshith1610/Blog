
from django.contrib import admin
from .models import *
admin.site.register(User)
admin.site.register(Comment)
admin.site.register(Blog)
admin.site.register(BlogMedia)
admin.site.register(CodeBlock)
admin.site.register(Tags)
# Register your models here.