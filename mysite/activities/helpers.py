
from .models import Mention,Activity
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.exceptions import ObjectDoesNotExist
import re
from netizen import models as netizen_models
from comments import models as comment_models

def do_like(content_type,object_id,user):
    is_liked = False
    if Activity.objects.filter(content_type=content_type,object_id=object_id, activity_type=Activity.LIKE, user=user).exists():
        Activity.objects.get(content_type=content_type,object_id=object_id, activity_type=Activity.LIKE, user=user).delete()    
        is_liked = False 
    else:
        Activity.objects.create(content_type=content_type,object_id=object_id, activity_type=Activity.LIKE, user=user)
        is_liked = True
    return(is_liked)

def do_bookmark(content_type,object_id,user):
    is_bookmarked = False
    if Activity.objects.filter(content_type=content_type,object_id=object_id, activity_type=Activity.BOOKMARK, user=user).exists():
        Activity.objects.get(content_type=content_type,object_id=object_id, activity_type=Activity.BOOKMARK, user=user).delete()    
        is_bookmarked = False 
    else:
        Activity.objects.create(content_type=content_type,object_id=object_id, activity_type=Activity.BOOKMARK, user=user)
        is_bookmarked = True
    return(is_bookmarked)



def get_total_likes(content_type_model,object_id):
    content_type = ContentType.objects.get(model=content_type_model)
    return Activity.objects.filter(content_type=content_type,object_id=object_id, activity_type=Activity.LIKE).count()

def get_total_favourites(content_type_model,object_id):
    content_type = ContentType.objects.get(model=content_type_model)
    return Activity.objects.filter(content_type=content_type,object_id=object_id, activity_type=Activity.BOOKMARK).count()

def is_liked(content_type_model,object_id,user):
    content_type = ContentType.objects.get(model=content_type_model)
    is_liked = Activity.objects.filter(content_type=content_type,object_id=object_id, activity_type=Activity.LIKE, user=user).exists() 

    return(is_liked)

def is_bookmarked(content_type_model,object_id,user):
    content_type = ContentType.objects.get(model=content_type_model)
    is_bookmarked = Activity.objects.filter(content_type=content_type,object_id=object_id, activity_type=Activity.BOOKMARK, user=user).exists() 

    return(is_bookmarked)

def checkForUsernames(text):
    usernames =[username[1:] for username in re.findall("@\w+",text)]
    
    if len(usernames)>0:
        return usernames
    else:
        return None


def mention(content_type_model,object_id,current_user,text):
    usernames = checkForUsernames(text)
    if usernames is not  None:
        content_type = ContentType.objects.get(model=content_type_model)
        for username in usernames:
            try:
                user = User.objects.get(username=username)
                Mention.objects.create(content_type=content_type,object_id=object_id,user=current_user,user_tagged=user)
            except User.DoesNotExist:
                pass


def change_username_in_text(new_username,previous_username,text):
    new_text = text.replace(previous_username,new_username)
    return new_text
    
def update(previous_username,new_username):
    tagged_user = User.objects.get(username=previous_username)

    mentions = Mention.objects.filter(user_tagged=tagged_user,)
    for mention in mentions:
        content_type = ContentType.objects.get(model=mention.content_type.model)
        obj = content_type.get_object_for_this_type(id=mention.object_id)
        print("update ",content_type.name)
        if content_type.name == "meme":
            new_text = change_username_in_text(new_username=new_username,previous_username=previous_username,text=obj.description)
            obj.description = new_text
            obj.save()
        elif content_type.name == "template":
            new_text = change_username_in_text(new_username=new_username,previous_username=previous_username,text=obj.description)
            obj.description = new_text
            obj.save()
        elif content_type.name == "comment" :
            new_text = change_username_in_text(new_username=new_username,previous_username=previous_username,text=obj.body)
            obj.body =new_text
            obj.save()
        else:
            return False
    return True