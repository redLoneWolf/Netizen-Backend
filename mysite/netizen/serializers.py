from .models import Template,Meme,ImageModel
from rest_framework import serializers
from comments.serializers import CommentSerializer
from comments.models import Comment
from activities.helpers import is_liked,is_bookmarked
from relationships.helpers import is_following
class TemplateListSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()
  
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Template
        fields = ['id','images','description','username','created','user_id','is_liked','likes','is_bookmarked','content_type']  

    def get_images(self,obj):
        return ImageSerializer(ImageModel.objects.filter(object_id=obj.id,content_type_id=obj.get_content_type_id),many=True).data

    def get_is_liked(self,obj):
        user = self.context['request'].user
        return is_liked(obj.get_content_type_model,obj.id,user)

    def get_is_bookmarked(self,obj):
        user = self.context['request'].user
        return is_bookmarked(obj.get_content_type_model,obj.id,user)

    def get_username(self, obj):
        return obj.user.username    

    def get_likes(self, obj):
        return obj.total_likes

    def get_content_type(self, obj):
        return obj.get_content_type_model 

class TemplatePatchSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Template
        fields = ['id','description']



class TemplateDetailSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    class Meta:
        model = Template
        fields = ['id','images','description','created','username','user_id','is_liked','is_following','likes','is_bookmarked','content_type','comments']  

    def get_is_following(self,obj):
        current_user = self.context['request'].user
        obj_user = obj.user
        print(current_user)
        return is_following(current_user,obj_user)

    def get_is_liked(self,obj):
        user = self.context['request'].user
        return is_liked(obj.get_content_type_model,obj.id,user)

    def get_is_bookmarked(self,obj):
        user = self.context['request'].user
        return is_bookmarked(obj.get_content_type_model,obj.id,user)

    def get_username(self, obj):
        return obj.user.username    

    def get_likes(self, obj):
        return obj.total_likes

    def get_content_type(self, obj):
        return obj.get_content_type_model      

    def get_images(self,obj):
        return ImageSerializer(ImageModel.objects.filter(object_id=obj.id,content_type_id=obj.get_content_type_id),many=True).data
    def get_comments(self,obj):
        return CommentSerializer(Comment.objects.filter(object_id=obj.id,content_type_id=obj.get_content_type_id,parent_id=None),many=True).data   

  


class TemplateUploadSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = Template
        fields = ['id','description']      

class ImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField() 
    class Meta:
        model = ImageModel
        fields = ['id','image']  
            



class MemeListSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Meme
        fields = ['id','images','description','created','username','user_id','is_following','is_liked','likes','is_bookmarked','content_type','comments']   


    def get_images(self,obj):
        return ImageSerializer(ImageModel.objects.filter(object_id=obj.id,content_type_id=obj.get_content_type_id),many=True).data

    def get_is_liked(self,obj):
     
        user = self.context['request'].user
        return is_liked(obj.get_content_type_model,obj.id,user)

    def get_is_following(self,obj):
        user = self.context['request'].user
        obj_user = obj.user
        return  is_following(user,obj_user)

    def get_is_bookmarked(self,obj):
        user = self.context['request'].user
        return is_bookmarked(obj.get_content_type_model,obj.id,user)

    def get_username(self, obj):
        return obj.user.username    

    def get_likes(self, obj):
        return obj.total_likes

    def get_content_type(self, obj):
        return obj.get_content_type_model 

    def get_comments(self,obj):
        return CommentSerializer(Comment.objects.filter(object_id=obj.id,content_type_id=obj.get_content_type_id,parent_id=None)[:3],many=True).data   

# class UserMemeSerializer(serializers.ModelSerializer):
   
#     class Meta:
#         model = Meme
#         fields =['id','images']
    

# class UserTemplateSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Template
#         fields =['id','images']
   
    

class MemeUploadSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Meme
        fields = ['id','images','description']

class MemePatchSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Meme
        fields = ['id','description']

class MemeDetailSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    class Meta:
        model = Meme
        fields = ['images','description','username','created','content_type','user_id','id','is_liked','is_following','likes','is_bookmarked','comments']  

 
    def get_images(self,obj):
        return ImageSerializer(ImageModel.objects.filter(object_id=obj.id,content_type_id=obj.get_content_type_id),many=True).data
        
    def get_username(self, obj):
        return obj.user.username    

    def get_is_following(self,obj):
        user = self.context['request'].user
        obj_user = obj.user
        return  is_following(user,obj_user)

    def get_content_type(self, obj):
        return obj.get_content_type_model 

    def get_is_liked(self,obj):
      
        user = self.context['request'].user
        return is_liked(obj.get_content_type_model,obj.id,user)
                  
    def get_likes(self, obj):
        return obj.total_likes 

    def get_is_bookmarked(self,obj):
        user = self.context['request'].user
        return is_bookmarked(obj.get_content_type_model,obj.id,user)

    def get_comments(self,obj):
        return CommentSerializer(Comment.objects.filter(object_id=obj.id,content_type_id=obj.get_content_type_id,parent_id=None),many=True).data   