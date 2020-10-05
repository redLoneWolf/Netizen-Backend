from django.db import models

from django.contrib.auth import get_user_model
User = get_user_model()
from django.core.exceptions import ValidationError
from django.utils import timezone

class UserFollowing(models.Model):
    follower  = models.ForeignKey(User, related_name="following",on_delete=models.CASCADE)

    followee  = models.ForeignKey(User, related_name="followers",on_delete=models.CASCADE)

    # You can even add info about when user started following
    created = models.DateTimeField(auto_now_add=True)     

    class Meta:
        unique_together = ("follower", "followee")
        ordering = ["-created"]   
    
    def save(self, *args, **kwargs):
        # Ensure users can't be friends with themselves
        if self.follower == self.followee:
            raise ValidationError("Users cannot follow themselves.")
        super(UserFollowing, self).save(*args, **kwargs)


class BlockManager(models.Manager):
    """ Following manager """

    def get_blockers(self, user):
      
        qs = Block.objects.filter(blocked=user).all()
        blockers =  User.objects.filter(id__in=qs.values('blocker_id'))
        return blockers

    def get_blocked_users(self, user):
        """ Return a list of all users the given user blocks """
        qs = Block.objects.filter(blocker=user).all()
        blocked = User.objects.filter(id__in=qs.values('blocked_id'))
        return blocked

    def add_block(self, blocker, blocked):
        """ Create 'follower' follows 'followee' relationship """
        if blocker == blocked:
            raise ValidationError("Users cannot block themselves")

        relation, created = Block.objects.get_or_create(
            blocker=blocker, blocked=blocked
        )

        if created is False:
            raise ValidationError(
                "User '%s' already blocks '%s'" % (blocker, blocked)
            )

        return relation

    def remove_block(self, blocker, blocked):
        """ Remove 'blocker' blocks 'blocked' relationship """
        try:
            rel = Block.objects.get(blocker=blocker, blocked=blocked)

            rel.delete()
 
            return True
        except Block.DoesNotExist:
            return False

    def is_blocked(self, blocker, blocked):
        """ Are these two users blocked? """
        try:
            Block.objects.get(blocker=blocker, blocked=blocked)
            return True
        except Block.DoesNotExist:
            return False

class Block(models.Model):
    """ Model to represent Following relationships """

    blocker = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blocking"
    )
    blocked = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="blockees"
    )
    created = models.DateTimeField(default=timezone.now)

    objects = BlockManager()

    class Meta:
        verbose_name = ("Blocked Relationship")
        verbose_name_plural = ("Blocked Relationships")
        unique_together = ("blocker", "blocked")

    def __str__(self):
        return "User #%s blocks #%s" % (self.blocker_id, self.blocked_id)

    def save(self, *args, **kwargs):
        # Ensure users can't be friends with themselves
        if self.blocker == self.blocked:
            raise ValidationError("Users cannot block themselves.")
        super(Block, self).save(*args, **kwargs)