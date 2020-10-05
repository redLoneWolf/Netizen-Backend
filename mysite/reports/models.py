from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
User = get_user_model()

from django.contrib.contenttypes.fields import GenericForeignKey

class ContentReport(models.Model):



    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField() 

    user = models.ForeignKey(User,on_delete=models.CASCADE,null=True,)

    

    content_object = GenericForeignKey()

    subject = models.TextField(blank=True)

    description = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)


class UserReport(models.Model):



    user = models.ForeignKey(User,on_delete=models.CASCADE)

    reporter = models.ForeignKey(User,on_delete=models.CASCADE,related_name='reporter')



    subject = models.TextField(blank=True)

    description = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)


