from rest_framework import serializers
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework.validators import UniqueValidator
from netizen.models import Template,Meme

from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from netizen.serializers import UserMemeSerializer,UserTemplateSerializer

from relationships.serializers import FollowingSerializer,FollowersSerializer

from relationships.helpers import is_following

class UserSerializer(serializers.ModelSerializer):
        
        template_count = serializers.SerializerMethodField()
        meme_count = serializers.SerializerMethodField()
        
        # templates =  serializers.SerializerMethodField()
        # memes =  serializers.SerializerMethodField()

        following = serializers.SerializerMethodField()
        followers = serializers.SerializerMethodField()    

        following_count = serializers.SerializerMethodField()
        followers_count = serializers.SerializerMethodField()   
        is_following = serializers.SerializerMethodField()

        # email = serializers.EmailField(required=True,
        #         validators=[UniqueValidator(queryset=User.objects.all())]
        #         )

        username = serializers.CharField(
                validators=[UniqueValidator(queryset=User.objects.all())]
                )

        class Meta:
                model = User
                fields = ['id','username','profile_pic','about','following_count','followers_count','is_following','following','followers','template_count','meme_count' ]

        def get_is_following(self,another_user):
                logged_user = self.context['request'].user
                return is_following(logged_user,another_user)

        def get_following(self,user):
                return  FollowingSerializer(user.following.all(), many=True).data  

        def get_followers(self, user):
                return FollowersSerializer(user.followers.all(), many=True).data 

        def get_following_count(self,user):
                return  user.following.count()

        def get_followers_count(self, user):
                return user.followers.count()      

        def get_template_count(self,user):
                return user.templates.count()

        def get_meme_count(self,user):
                return user.memes.count()
        # def get_memes(self,obj):
        #     return UserMemeSerializer(obj.memes, many=True).data 
        # def get_templates(self,obj):
        #     return UserTemplateSerializer(obj.templates, many=True).data 

class UserUpdateSerializer(serializers.ModelSerializer):
        class Meta :
                model = User
                fields = ['username','about']

class UserQuerSerializer(serializers.ModelSerializer):
        class Meta :
                model = User
                fields = ['username','profile_pic']

class RegistrationSerializer(serializers.ModelSerializer):
        email2 = serializers.EmailField(label="confirm email")
       

        class Meta:
                model = User
                fields = ['email','email2', 'username', 'password']
                extra_kwargs = {
                'password': {'write_only': True},
                'password2':{'write_only':True},
                }	

        def save(self):
                email = self.validated_data['email']
                print(email)
                email2 = self.validated_data['email2']
                if email != email2:
                        raise serializers.ValidationError({'email': 'email must match.'})
                password = self.validated_data['password']
               
                
                user = User(
                                        email=self.validated_data['email'],
                                        username=self.validated_data['username']
                                )
                try:
                        password_validation.validate_password(password,user)
                except ValidationError as e :
                        raise serializers.ValidationError(e.messages)

                user.set_password(password)
                user.save()
                return user

class PasswordSerializer(serializers.Serializer):
        old_password = serializers.CharField(required=True,write_only=True,style={'input_type': 'password'})
        new_password = serializers.CharField(required=True,write_only=True,style={'input_type': 'password'})
        new_password2 = serializers.CharField(required=True,write_only=True,style={'input_type': 'password'})

       