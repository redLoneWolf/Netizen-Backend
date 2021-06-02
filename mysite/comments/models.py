from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
User = get_user_model()

from django.contrib.contenttypes.fields import GenericForeignKey
import uuid

from utils.fields import RandomB64Field
class CommentManager(models.Manager):
    def all(self):
        qs = super(CommentManager, self).filter(parent=None)
        return qs

    def filter_by_instance(self, instance):
        content_type = ContentType.objects.get_for_model(instance.__class__)
        obj_id = instance.id
        # print(obj_id)
        qs = super(CommentManager, self).filter(content_type=content_type, object_id= obj_id).filter(parent=None)
        return qs


class Comment(models.Model):
    id = RandomB64Field(primary_key=True,  auto=True,unique=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = RandomB64Field(editable=False,auto=False) 

    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True)
    content_object = GenericForeignKey()


    
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    # manually deactivate inappropriate comments from admin site
    active = models.BooleanField(default=True)
    parent = models.ForeignKey('self', null=True,blank=True,on_delete=models.CASCADE,related_name='replies')
    

    class Meta:
        # sort comments in chronological order by default
        ordering = ('-created',)

    

    objects = CommentManager()


    @property
    def get_replies(self): #replies
        return self.replies.filter(parent=self)

    @property
    def is_parent(self):
        if self.parent is not None:
            return False
        return True