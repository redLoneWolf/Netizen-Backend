from .models import UserFollowing,Block
from django.contrib.auth import get_user_model
User = get_user_model()



def is_following(current_user,user_to_follow):

     return(UserFollowing.objects.filter(follower =current_user,followee =user_to_follow).exists())

def do_folllow(current_user,user_to_follow):
    following = False
    if is_following(current_user =current_user,user_to_follow =user_to_follow):
        UserFollowing.objects.get(follower =current_user,followee =user_to_follow).delete()    
        following = False 
    else:
        UserFollowing.objects.create(follower =current_user,followee =user_to_follow)
        following = True
    return(following)

def unfollow_both_users_blocked(current_user,user_to_follow):
    if is_following(current_user =current_user,user_to_follow =user_to_follow):
        UserFollowing.objects.get(follower =current_user,followee =user_to_follow).delete()  
    if is_following(current_user =user_to_follow,user_to_follow =current_user):
        UserFollowing.objects.get(follower =user_to_follow,followee =current_user).delete()   

def is_blocked(current_user,user_to_block):

     return(Block.objects.is_blocked(blocker =current_user,blocked =user_to_block))

def get_blockers(user):
    return (Block.objects.get_blockers(user))  

def get_blocked_users(user):
    return (Block.objects.get_blocked_users(user))


def do_block(blocker_user,blocked_user):
    blocked = False
    if is_blocked(current_user = blocker_user,user_to_block = blocked_user):
        Block.objects.remove_block(blocker =blocker_user,blocked =blocked_user)  
        blocked = False 
    else:
        Block.objects.add_block(blocker =blocker_user,blocked =blocked_user)   
        unfollow_both_users_blocked(blocker_user,blocked_user)
        blocked = True
    return(blocked)



