from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid

from utils.fields import RandomB64Field
class Activity(models.Model):
    BOOKMARK = 'B'
    LIKE = 'L'
   
    
    ACTIVITY_TYPES = (
        (BOOKMARK, 'Bookmark'),
        (LIKE, 'Like'),
       
        
    )

    user = models.ForeignKey(User,on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=1, choices=ACTIVITY_TYPES)
    date = models.DateTimeField(auto_now_add=True)

    # Below the mandatory fields for generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id =  RandomB64Field(editable=False,auto=False) 
    content_object = GenericForeignKey()

class Mention(models.Model):
    id = RandomB64Field(primary_key=True, editable=False,auto=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = RandomB64Field(editable=False,auto=False) 

    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    content_object = GenericForeignKey()


    
    user_tagged = models.ForeignKey(User,on_delete=models.CASCADE,null=True,related_name='users_tagged')
    created = models.DateTimeField(auto_now_add=True)


    active = models.BooleanField(default=True)

    class Meta:

        ordering = ('-created',)
