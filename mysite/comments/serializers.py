from rest_framework import serializers
from .models import Comment

class CommentCreateSerializer(serializers.ModelSerializer):
    
    object_id = serializers.SerializerMethodField()

    username  =  serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['id','object_id','body','username'] 
 

    def get_object_id(self,comment):
        return comment.object_id    

    def get_username(self,comment):
        return comment.user.username           

class ReplySerializer(serializers.ModelSerializer):
    body = serializers.SerializerMethodField()  
    username  = serializers.SerializerMethodField() 
    comment_id = serializers.SerializerMethodField() 
    class Meta:
        model = Comment
        fields = ['comment_id','parent_id','username','body']

    def get_body(self, reply):
        return reply.body   
    def get_username(self,reply):
        return reply.user.username
    def get_comment_id(self,reply):
        return reply.id     

class CommentSerializer(serializers.ModelSerializer):
    body = serializers.SerializerMethodField() 
    replies = serializers.SerializerMethodField()   
    replies_count= serializers.SerializerMethodField() 
    username  = serializers.SerializerMethodField() 

 
    
    class Meta:
        model = Comment
        fields =['id','username','user_id','body','created','replies_count','replies',]

    

    def get_replies(self, comment):
        # print(comment.replies.all)
        # return ReplySerializer(comment.replies.filter(parent=comment,active=True),many=True).data
        return CommentSerializer(comment.replies.filter(parent=comment,active=True),many=True).data
    def get_replies_count(self, comment):
        # print(comment.replies.all)
        return comment.replies.count()

    def get_body(self, comment):
        return comment.body   
    def get_username(self,comment):
        return comment.user.username
    


