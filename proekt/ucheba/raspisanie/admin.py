from django.contrib import admin
from .models import Profile, LoginLog

admin.site.register(Profile)
admin.site.register(LoginLog)
