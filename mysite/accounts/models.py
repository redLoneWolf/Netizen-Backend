
from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.validators import RegexValidator
from .managers import CustomUserManager
from django.templatetags.static import static
import os.path
from PIL import Image as img
from io import BytesIO
from django.core.mail import send_mail

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

THUMB_SIZE = 64,64



class CustomUser(AbstractBaseUser, PermissionsMixin):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
    )
   
    email = models.EmailField(unique=True, null=True)
    email_confirmed = models.BooleanField(default=False)
    username = models.CharField(unique=True, max_length=100, null=False)
    first_name = models.CharField(max_length=100, null=True)
    last_name = models.CharField(max_length=100, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    birthday = models.DateField(null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True, null=True)
    about = models.TextField(max_length=2000)
    location = models.CharField(max_length=100, blank=True)
    profile_pic = models.ImageField(
        upload_to='media/profile/', null=True)
    
    thumbnail = models.ImageField(
        upload_to='media/profile/thumbs/', editable=False, default="HI")
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. ''Unselect this instead of deleting accounts.'
        ),
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)
    objects = CustomUserManager()

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering=['-date_joined'] 

    def get_full_name(self):
        return self.get_full_name()

    # def get_short_name(self):
    #     return self.get_full_name()

    

    def __str__(self):
        return self.username

    def get_profile_url(self):
        return self.username
        
    def email_user(self, subject, message, from_email=None, **kwargs):
        '''
        Sends an email to this User.
        '''
        send_mail(subject, message, from_email, [self.email], **kwargs)
    
    @property
    def profile_picture_url(self):
        if self.profile_pic and hasattr(self.profile_pic, 'url'):
            return self.profile_pic.url
        else:
            return static('avatar/avatar.jpg')

    


    @property
    def profile_thumbnail_url(self):
        if self.thumbnail and hasattr(self.thumbnail, 'url'):
            return self.thumbnail.url
        else:
            return static('avatar/avatar.jpg')


    def save(self, *args, **kwargs):
        if self.profile_pic:
            if not self.make_thumbnail():
                # set to a default thumbnail
                raise Exception('Could not create thumbnail - is the file type valid?')

        super(CustomUser, self).save(*args, **kwargs)

    def make_thumbnail(self):

        image = img.open(self.profile_pic)
        #image.thumbnail(THUMB_SIZE, img.ANTIALIAS)
        image = image.resize(THUMB_SIZE, img.ANTIALIAS)

        thumb_name, thumb_extension = os.path.splitext(self.profile_pic.name)
        thumb_extension = thumb_extension.lower()

        thumb_filename = thumb_name + '_thumb' + thumb_extension

        if thumb_extension in ['.jpg', '.jpeg']:
            FTYPE = 'JPEG'
        elif thumb_extension == '.gif':
            FTYPE = 'GIF'
        elif thumb_extension == '.png':
            FTYPE = 'PNG'
        else:
            return False    # Unrecognized file type

        # Save thumbnail to in-memory file as StringIO
        temp_thumb = BytesIO()
        quality_val = 90
        #image.save(filename, 'JPEG', quality=quality_val)
        image.save(temp_thumb, FTYPE, quality=quality_val)
        temp_thumb.seek(0)

        # set save=False, otherwise it will run in an infinite loop
        self.thumbnail.save(thumb_filename, ContentFile(
            temp_thumb.read()), save=False)
        temp_thumb.close()

        return True

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)



