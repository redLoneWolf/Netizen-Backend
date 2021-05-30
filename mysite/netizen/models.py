from django.db import models

import uuid
from django.db import models
import os.path
from PIL import Image as img
from io import BytesIO

from django.urls import reverse
from django.core.files.base import ContentFile
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
User = get_user_model()
from activities.helpers import get_total_favourites,get_total_likes,is_liked
from comments.models import Comment

from django_extensions.db.fields  import ShortUUIDField


THUMB_SIZE = 304, 255
from django.contrib.contenttypes.fields import GenericForeignKey

def get_template_images_path(instance,filename):
    id = instance.id
    ext = filename.split(".")[-1]
    if instance.content_type == ContentType.objects.get_for_model(model=Meme):
        return "netizen/memes/{id}.{ext}".format(id=id,ext=ext)
    elif instance.content_type == ContentType.objects.get_for_model(model=Template):
        return "netizen/templates/{id}.{ext}".format(id=id,ext=ext)

def get_template_thumbnail_path(instance,filename):
    id = instance.id
    ext = filename.split(".")[-1]
    # print(ext)
    if instance.content_type == ContentType.objects.get_for_model(model=Meme):
        return "netizen/memes/thumbs/{id}_thumb.{ext}".format(id=id,ext=ext)
    elif instance.content_type == ContentType.objects.get_for_model(model=Template):
        return "netizen/templates/thumbs/{id}_thumb.{ext}".format(id=id,ext=ext)

class ImageModel(models.Model):
    id = ShortUUIDField(primary_key=True, auto=True, editable=False)
   
    image = models.ImageField(upload_to=get_template_images_path, blank=False,null=False)
    thumbnail = models.ImageField(
        upload_to=get_template_thumbnail_path, blank=False, default='hi')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = ShortUUIDField(editable=False,auto=False) 
    content_object = GenericForeignKey()


    def save(self, *args, **kwargs):
        if not self.make_thumbnail():
            # set to a default thumbnail
            raise Exception(
                'Could not create thumbnail - is the file type valid?')

        super(ImageModel, self).save(*args, **kwargs)



    def make_thumbnail(self):
        try:
            image = img.open(self.image)
            #image.thumbnail(THUMB_SIZE, img.ANTIALIAS)
            image = image.resize(THUMB_SIZE, img.ANTIALIAS)

            thumb_name, thumb_extension = os.path.splitext(self.image.name)
            # print(thumb_name)
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
            # print(thumb_filename)
            self.thumbnail.save(thumb_filename, ContentFile(
                temp_thumb.read()), save=False)
            temp_thumb.close()

            return True
        except IOError:
            print("cannot create thumbnail ")
            return False


class Template(models.Model):
    id = ShortUUIDField(primary_key=True, auto=True, editable=False)
    user = models.ForeignKey(User, related_name='templates', on_delete=models.CASCADE)
    description = models.TextField(max_length=250,blank=True)
    created = models.DateTimeField(auto_now_add=True)
    images = GenericRelation(ImageModel)
    comment = GenericRelation(Comment)
    class Meta:
        ordering = ['-created']
    
    def total_favourites(self):
        return get_total_favourites(self.get_content_type,self.id)
    @property
    def total_likes(self):

        return get_total_likes(self.get_content_type_model,self.id)
        
    def get_absolute_url(self):
        url = reverse('netizen:templates',kwargs={'id':self.id})
        return url

    @property
    def get_content_type_id(self):  
        content_type = ContentType.objects.get_for_model(model=Template)
        return content_type.id
    
    @property
    def get_content_type(self):  
        content_type = ContentType.objects.get_for_model(model=Template)
        return content_type

    @property
    def get_content_type_model(self):  
        content_type = ContentType.objects.get_for_model(model=Template)
        return content_type.model




class Meme(models.Model):
    id = ShortUUIDField(primary_key=True, auto=True, editable=False)
    user = models.ForeignKey(User, related_name='memes',
                             on_delete=models.CASCADE)
    template = models.ForeignKey(
        Template, related_name='memes', blank=True, on_delete=models.CASCADE,null=True)

    # images = models.ImageField(upload_to='netizen/memes',)
    description = models.TextField(max_length=250,blank=True)
    # thumbnail = models.ImageField(
    #     upload_to='netizen/memes/thumbs', blank=False, default='hi')
    created = models.DateTimeField(auto_now_add=True)
    comment = GenericRelation(Comment)
    images = GenericRelation(ImageModel)


    @property
    def total_likes(self):
        return get_total_likes(self.get_content_type_model,self.id)
        
   


    class Meta:
        ordering = ['-created']

    def get_absolute_url(self):
        url = reverse('netizen:memes',kwargs={'id':self.id})
        return url

    def get_comments(self):
        queryset = Comment.objects.filter(object_id=self.id,content_type_id=self.get_content_type_id,parent_id=None)
        # print(queryset)
        return queryset
    @property
    def get_content_type_id(self):  
        content_type = ContentType.objects.get_for_model(model=Meme)
        return content_type.id

    @property
    def get_content_type(self):  
        content_type = ContentType.objects.get_for_model(model=Meme)
        return content_type 
    
    @property
    def get_content_type_model(self):  
        content_type = ContentType.objects.get_for_model(model=Meme)
        return content_type.model






