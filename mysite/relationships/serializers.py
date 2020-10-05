from.models import UserFollowing
from rest_framework import serializers

class FollowingSerializer(serializers.ModelSerializer):
        username = serializers.SerializerMethodField()
        profile_pic = serializers.SerializerMethodField()
        class Meta:
                model = UserFollowing
                fields = [ "username","profile_pic" ]
        def get_username(self,obj):
                return obj.followee.username
        def get_profile_pic(self,obj):
                return 1


class FollowersSerializer(serializers.ModelSerializer):
        username = serializers.SerializerMethodField()
        profile_pic = serializers.SerializerMethodField()
        class Meta:
                model = UserFollowing
                fields = [ "username","profile_pic" ]
        def get_username(self,obj):
                return obj.follower.username

        def get_profile_pic(self,obj):
                return 1  