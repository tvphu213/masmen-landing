from django.contrib import admin
from blog.models import Company
from blog.models import Server

# Register your models here.
admin.site.register(Company)
admin.site.register(Server)