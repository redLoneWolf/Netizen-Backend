from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import CustomUser

class AccountsAdmin(UserAdmin):
    
    list_display = ('username','email', 'is_staff', 'is_active','profile_pic')
    list_filter = ( 'is_staff', 'is_active','is_superuser','date_joined','gender',)
    search_fields = ('email',)
    readonly_fields = ['date_joined','last_login','profile_pic']
  





admin.site.register(CustomUser,AccountsAdmin)
