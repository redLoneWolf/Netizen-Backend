from django.contrib.auth.models import BaseUserManager
from django.db import models


class CustomUserManager(BaseUserManager):
    """Overriding BaseUserManager in order to allow users to register and authenticate by using email instead of username """
    
    def create_user(self, email, username,password=None,first_name=None,last_name=None, **kwargs):
        if not email and first_name:
            raise ValueError('Email and firstname field is required')

        email = self.normalize_email(email)
        user = self.model(email=email, **kwargs)
        user.username=username
        user.first_name=first_name
        user.last_name=last_name
        
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, username,password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, username,  password, **extra_fields)