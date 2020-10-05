
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase,APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import Template,Meme
from activities.models import Activity
from comments.models import Comment
from PIL import Image
import tempfile

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class TemplateUploadTests(APITestCase):
    template_create_url = reverse('netizen:template_upload')


    def setUp(self):
        self.user = User.objects.create(email='test2@2.com',username='testusername')
        self.user.set_password('testpassword123')
        self.user.save()

        image = Image.new('RGB', (100, 100))

        self.tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(self.tmp_file)
        self.tmp_file.seek(0)
        self.test_description =  'description teste tstttfvgs'
        self.data = {'images':self.tmp_file,'description':self.test_description}
        

    def test_create_template(self):
      
        self.client.force_authenticate(self.user)
        response = self.client.post(self.template_create_url, self.data, format='multipart')

        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
 
        self.assertEqual(response.data['username'],self.user.username )
        self.assertEqual(response.data['description'],self.test_description )

    def test_create_template_without_credentials(self):
        response = self.client.post(self.template_create_url, self.data, format='multipart')

        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
    
    def test_create_template_without_images(self):
        data ={'description':self.test_description}
        self.client.force_authenticate(self.user)
        response = self.client.post(self.template_create_url, data, format='multipart')

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
 
    def test_create_template_with_other_extensions(self):
        data ={'description':self.test_description}
        self.client.force_authenticate(self.user)

        fp=tempfile.NamedTemporaryFile(suffix='.exe')
        fp.write(b'Hello guys')
        fp.seek(0)
        data={'images':fp,'description':self.test_description}

        response = self.client.post(self.template_create_url, data, format='multipart')

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

class TemplateViewTests(APITestCase):
    
    
    
    def setUp(self):
        self.user = User.objects.create(email='test2@2.com',username='testusername')
        self.user.set_password('testpassword123')
        self.user.save()
        self.token = get_tokens_for_user(self.user)
        image = Image.new('RGB', (100, 100))

        self.tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(self.tmp_file)
        self.tmp_file.seek(0)
        self.test_description =  'description teste tstttfvgs'

        template_create_url = reverse('netizen:template_upload')
        data = {'images':self.tmp_file,'description':self.test_description}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token['access'])
        response = self.client.post(template_create_url, data, format='multipart')

        self.template_id = response.data['id']
        self.template_detail_url = reverse('netizen:template_detail',kwargs={'id':self.template_id}) 
        self.template = Template.objects.get(id=self.template_id)
    
    
    def test_detail_with_credentials(self):
      
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token['access'])
        response = self.client.get(self.template_detail_url)

        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertTrue('comments' in response.data )
        self.assertTrue('username' in response.data )
        self.assertTrue('content_type' in response.data )
        self.assertTrue('likes' in response.data )
        self.assertTrue('id' in response.data )
        self.assertTrue('images' in response.data )
        
        self.assertEqual(response.data['content_type'],self.template.get_content_type_model)
 
        self.assertEqual(response.data['username'],self.user.username )
        self.assertEqual(response.data['description'],self.test_description )


        data = {'description':'modified description'}
        response = self.client.patch(self.template_detail_url,data, format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['description'],data['description'])

        

        response = self.client.delete(self.template_detail_url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_detail_without_credentials(self):
      
        # self.client.force_authenticate(self.user)
        self.client.credentials()
        response = self.client.get(self.template_detail_url)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
        self.client.credentials()
        
        data = {'description':'modified description'}
        response = self.client.patch(self.template_detail_url,data, format='json')
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
        self.client.credentials()
        
        response = self.client.delete(self.template_detail_url)
        
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
    
    def test_detail_with_other_credentials(self):
        other_user = User.objects.create(email='test2@3.com',username='testusername3')
        other_user.set_password('testpassword123')
        other_user.save()
        token = get_tokens_for_user(other_user)

        # self.client.force_authenticate(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' +token['access'])
        response = self.client.get(self.template_detail_url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token['access'])
        
        data = {'description':'modified description'}
        response = self.client.patch(self.template_detail_url,data, format='json')

        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token['access'])
        
        response = self.client.delete(self.template_detail_url)
        
        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)

class MemeUploadTests(APITestCase):
    meme_create_url = reverse('netizen:meme_upload')


    def setUp(self):
        self.user = User.objects.create(email='test2@2.com',username='testusername')
        self.user.set_password('testpassword123')
        self.user.save()

        image = Image.new('RGB', (100, 100))

        self.tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(self.tmp_file)
        self.tmp_file.seek(0)
        self.test_description =  'description teste tstttfvgs'
        self.data = {'images':self.tmp_file,'description':self.test_description}
        

    def test_create_template(self):
      
        self.client.force_authenticate(self.user)
        response = self.client.post(self.meme_create_url, self.data, format='multipart')

        self.assertEqual(response.status_code,status.HTTP_201_CREATED)
 
        self.assertEqual(response.data['username'],self.user.username )
        self.assertEqual(response.data['description'],self.test_description )

    def test_create_template_without_credentials(self):
        response = self.client.post(self.meme_create_url, self.data, format='multipart')

        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
    
    def test_create_template_without_images(self):
        data ={'description':self.test_description}
        self.client.force_authenticate(self.user)
        response = self.client.post(self.meme_create_url, data, format='multipart')

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
 
    def test_create_template_with_other_extensions(self):
        data ={'description':self.test_description}
        self.client.force_authenticate(self.user)

        fp=tempfile.NamedTemporaryFile(suffix='.exe')
        fp.write(b'Hello guys')
        fp.seek(0)
        data={'images':fp,'description':self.test_description}

        response = self.client.post(self.meme_create_url, data, format='multipart')

        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

class MemeViewTests(APITestCase):
    
    
    
    def setUp(self):
        self.user = User.objects.create(email='test2@2.com',username='testusername')
        self.user.set_password('testpassword123')
        self.user.save()
        self.token = get_tokens_for_user(self.user)
        image = Image.new('RGB', (100, 100))

        self.tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(self.tmp_file)
        self.tmp_file.seek(0)
        self.test_description =  'description teste tstttfvgs'

        meme_create_url = reverse('netizen:meme_upload')
        data = {'images':self.tmp_file,'description':self.test_description}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token['access'])

        response = self.client.post(meme_create_url, data, format='multipart')

        self.meme_id = response.data['id']
        self.meme_detail_url = reverse('netizen:meme_detail',kwargs={'id':self.meme_id}) 
        self.meme = Meme.objects.get(id=self.meme_id)
    
    
    def test_detail_with_credentials(self):
      
 
        response = self.client.get(self.meme_detail_url)
     

        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertTrue('comments' in response.data )
        self.assertTrue('username' in response.data )
        self.assertTrue('content_type' in response.data )
        self.assertTrue('likes' in response.data )
        self.assertTrue('id' in response.data )
        self.assertTrue('images' in response.data )
        self.assertEqual(response.data['content_type'],self.meme.get_content_type_model)
 
        self.assertEqual(response.data['username'],self.user.username )
        self.assertEqual(response.data['description'],self.test_description )
   


        data = {'description':'modified description'}
        response = self.client.patch(self.meme_detail_url,data, format='json')      # patch
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['description'],data['description'])
    

        

        response = self.client.delete(self.meme_detail_url)                     # delete
        self.assertEqual(response.status_code,status.HTTP_200_OK)

    def test_detail_without_credentials(self):
      
        # self.client.force_authenticate(self.user)
        self.client.credentials()
        response = self.client.get(self.meme_detail_url)                        # get
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
        self.client.credentials()
        
        data = {'description':'modified description'}
        response = self.client.patch(self.meme_detail_url,data, format='json')
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)                  # patch
        self.client.credentials()
        
        response = self.client.delete(self.meme_detail_url)
        
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)          # delete
    
    def test_detail_with_other_credentials(self):
        other_user = User.objects.create(email='test2@3.com',username='testusername3')           # get
        other_user.set_password('testpassword123')
        other_user.save()
        token = get_tokens_for_user(other_user)

        # self.client.force_authenticate(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' +token['access'])
        response = self.client.get(self.meme_detail_url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
     
        
        data = {'description':'modified description'}
        response = self.client.patch(self.meme_detail_url,data, format='json')          # patch

        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)

        
        response = self.client.delete(self.meme_detail_url)                         # delete
        
        self.assertEqual(response.status_code,status.HTTP_403_FORBIDDEN)




class ActivityTests(APITestCase):
    like_url= reverse('activities:like')
    bookmark_url = reverse('activities:bookmark')

    def setUp(self):
        self.user = User.objects.create(email='test2@2.com',username='testusername')
        self.user.set_password('testpassword123')
        self.user.save()
        self.token = get_tokens_for_user(self.user)
        image = Image.new('RGB', (100, 100))
        self.tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(self.tmp_file)
        self.tmp_file.seek(0)
        self.test_description =  'description teste tstttfvgs'

        meme_create_url = reverse('netizen:meme_upload')
        data = {'images':self.tmp_file,'description':self.test_description}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token['access'])

        response = self.client.post(meme_create_url, data, format='multipart')
      
        self.meme_id = response.data['id']
        self.meme =Meme.objects.get(id=self.meme_id) 
        
        image = Image.new('RGB', (100, 100))
        self.tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(self.tmp_file)
        self.tmp_file.seek(0)
        template_create_url = reverse('netizen:template_upload')
        data = {'images':self.tmp_file,'description':self.test_description}
      

        response = self.client.post(template_create_url, data, format='multipart')
      
        self.template_id = response.data['id']
        self.template =Template.objects.get(id=self.template_id) 

    def test_like(self):
        data={'content_type':self.template.get_content_type_model,      
                'object_id':self.template.id}
        response = self.client.post(self.like_url, data, format='json')         # for like template
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['post'],self.template.id)
        self.assertEqual(response.data['is_liked'],True)
        self.assertEqual(response.data['likes'],1)
        self.assertTrue(Activity.objects.filter(content_type=self.template.get_content_type,object_id=self.template.id,activity_type=Activity.LIKE,user=self.user).exists())
        self.assertEqual(Activity.objects.filter(content_type=self.template.get_content_type,object_id=self.template.id,activity_type=Activity.LIKE).count(),1)

    
        response = self.client.post(self.like_url, data, format='json')         # for unlike template
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['post'],self.template.id)
        self.assertEqual(response.data['is_liked'],False)
        self.assertEqual(response.data['likes'],0)
        self.assertFalse(Activity.objects.filter(content_type=self.template.get_content_type,object_id=self.template.id,activity_type=Activity.LIKE,user=self.user).exists())
        self.assertEqual(Activity.objects.filter(content_type=self.template.get_content_type,object_id=self.template.id,activity_type=Activity.LIKE).count(),0)

        data={'content_type':self.meme.get_content_type_model,      
                'object_id':self.meme.id}
        response = self.client.post(self.like_url, data, format='json')         # for like meme

        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['post'],self.meme.id)
        self.assertEqual(response.data['is_liked'],True)
        self.assertEqual(response.data['likes'],1)
        self.assertTrue(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.LIKE,user=self.user).exists())
        self.assertEqual(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.LIKE).count(),1)


        response = self.client.post(self.like_url, data, format='json')         # for unlike meme
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['post'],self.meme.id)
        self.assertEqual(response.data['is_liked'],False)
        self.assertEqual(response.data['likes'],0)
        self.assertFalse(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.LIKE,user=self.user).exists())
        self.assertEqual(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.LIKE).count(),0)

    def test_like_without_credentials(self):
        self.client.credentials()
        data={'content_type':self.template.get_content_type_model,      
                'object_id':self.template.id}
        response = self.client.post(self.like_url, data, format='json')         # for like template
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
        
        self.assertFalse(Activity.objects.filter(content_type=self.template.get_content_type,object_id=self.template.id,activity_type=Activity.LIKE,user=self.user).exists())
        self.assertEqual(Activity.objects.filter(content_type=self.template.get_content_type,object_id=self.template.id,activity_type=Activity.LIKE).count(),0)


        response = self.client.post(self.like_url, data, format='json')         # for unlike template
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
       
        self.assertFalse(Activity.objects.filter(content_type=self.template.get_content_type,object_id=self.template.id,activity_type=Activity.LIKE,user=self.user).exists())
        self.assertEqual(Activity.objects.filter(content_type=self.template.get_content_type,object_id=self.template.id,activity_type=Activity.LIKE).count(),0)

        data={'content_type':self.meme.get_content_type_model,      
                'object_id':self.meme.id}
        response = self.client.post(self.like_url, data, format='json')         # for like meme
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
        
        self.assertFalse(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.LIKE,user=self.user).exists())
        self.assertEqual(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.LIKE).count(),0)

 
        response = self.client.post(self.like_url, data, format='json')         # for unlike meme
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
        
        self.assertFalse(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.LIKE,user=self.user).exists())
        self.assertEqual(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.LIKE).count(),0)

    def test_bookmark(self):
        data={'content_type':self.template.get_content_type_model,      
                'object_id':self.template.id}
        response = self.client.post(self.bookmark_url, data, format='json')         # for like template
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['post'],self.template.id)
        self.assertEqual(response.data['is_bookmarked'],True)
        
        self.assertTrue(Activity.objects.filter(content_type=self.template.get_content_type,object_id=self.template.id,activity_type=Activity.BOOKMARK,user=self.user).exists())
        self.assertEqual(Activity.objects.filter(content_type=self.template.get_content_type,object_id=self.template.id,activity_type=Activity.BOOKMARK).count(),1)

  
        response = self.client.post(self.bookmark_url, data, format='json')         # for unlike template
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['post'],self.template.id)
        self.assertEqual(response.data['is_bookmarked'],False)
        
        self.assertFalse(Activity.objects.filter(content_type=self.template.get_content_type,object_id=self.template.id,activity_type=Activity.BOOKMARK,user=self.user).exists())
        self.assertEqual(Activity.objects.filter(content_type=self.template.get_content_type,object_id=self.template.id,activity_type=Activity.BOOKMARK).count(),0)
        
        data={'content_type':self.meme.get_content_type_model,      
                'object_id':self.meme.id}

        response = self.client.post(self.bookmark_url, data, format='json')         # for like meme
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['post'],self.meme.id)
        self.assertEqual(response.data['is_bookmarked'],True)

        self.assertTrue(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.BOOKMARK,user=self.user).exists())
        self.assertEqual(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.BOOKMARK).count(),1)


        response = self.client.post(self.bookmark_url, data, format='json')         # for unlike meme
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['post'],self.meme.id)
        self.assertEqual(response.data['is_bookmarked'],False)
  
        self.assertFalse(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.BOOKMARK,user=self.user).exists())
        self.assertEqual(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.BOOKMARK).count(),0)

    def test_bookmark_without_credentials(self):
        self.client.credentials()
        data={'content_type':self.template.get_content_type_model,      
                'object_id':self.template.id}
        response = self.client.post(self.bookmark_url, data, format='json')         # for like template
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
        
        self.assertFalse(Activity.objects.filter(content_type=self.template.get_content_type,object_id=self.template.id,activity_type=Activity.BOOKMARK,user=self.user).exists())
        self.assertEqual(Activity.objects.filter(content_type=self.template.get_content_type,object_id=self.template.id,activity_type=Activity.BOOKMARK).count(),0)


        response = self.client.post(self.bookmark_url, data, format='json')         # for unlike template
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
       
        self.assertFalse(Activity.objects.filter(content_type=self.template.get_content_type,object_id=self.template.id,activity_type=Activity.BOOKMARK,user=self.user).exists())
        self.assertEqual(Activity.objects.filter(content_type=self.template.get_content_type,object_id=self.template.id,activity_type=Activity.BOOKMARK).count(),0)

        data={'content_type':self.meme.get_content_type_model,      
                'object_id':self.meme.id}
        response = self.client.post(self.bookmark_url, data, format='json')         # for like meme
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
        
        self.assertFalse(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.BOOKMARK,user=self.user).exists())
        self.assertEqual(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.BOOKMARK).count(),0)


        response = self.client.post(self.bookmark_url, data, format='json')         # for unlike meme
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
        
        self.assertFalse(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.BOOKMARK,user=self.user).exists())
        self.assertEqual(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.BOOKMARK).count(),0)


class CommentTests(APITestCase):
            
        # self.comment_update_url= reverse('comments:comment_update')
        # self.comment_delete_url= reverse('comments:comment_delete')

    def setUp(self):
        self.comment_create_url= reverse('comments:comment_create')
        self.user = User.objects.create(email='test2@2.com',username='testusername')
        self.user.set_password('testpassword123')
        self.user.save()
        self.token = get_tokens_for_user(self.user)

        image = Image.new('RGB', (100, 100))
        self.tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(self.tmp_file)
        self.tmp_file.seek(0)
        self.test_description =  'description teste tstttfvgs'

        meme_create_url = reverse('netizen:meme_upload')
        data = {'images':self.tmp_file,'description':self.test_description}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token['access'])

        response = self.client.post(meme_create_url, data, format='multipart')
      
        self.meme_id = response.data['id']
        self.meme =Meme.objects.get(id=self.meme_id)


        image = Image.new('RGB', (100, 100))
        self.tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(self.tmp_file)
        self.tmp_file.seek(0)
        template_create_url = reverse('netizen:template_upload')
        data = {'images':self.tmp_file,'description':self.test_description}
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token['access'])

        response = self.client.post(template_create_url, data, format='multipart')
      
        self.template_id = response.data['id']
        self.template =Template.objects.get(id=self.template_id)  
        
    def test_comment_create(self):
        data = {'content_type':self.meme.get_content_type_model,
                'object_id':self.meme.id,
                'body':'test test comments'}

        response = self.client.post(self.comment_create_url, data, format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertTrue('body' in response.data )
        self.assertTrue('object_id' in response.data )
        self.assertTrue('id' in response.data )
    
        self.assertEqual(response.data['body'],data['body'])
        self.assertEqual(response.data['object_id'],data['object_id'])


        data = {'content_type':self.template.get_content_type_model,
                'object_id':self.template.id,
                'body':'test test comments'}

        response = self.client.post(self.comment_create_url, data, format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertTrue('body' in response.data )
        self.assertTrue('object_id' in response.data )
        self.assertTrue('id' in response.data )
    
        self.assertEqual(response.data['body'],data['body'])
        self.assertEqual(response.data['object_id'],data['object_id'])


    def test_comment_create_without_credentials(self):
        data = {'content_type':self.meme.get_content_type_model,
                'object_id':self.meme.id,
                'body':'test test comments'}
        self.client.credentials()
        response = self.client.post(self.comment_create_url, data, format='json')
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

        self.assertFalse('body' in response.data )
        self.assertFalse('object_id' in response.data )
        self.assertFalse('id' in response.data )
    

        data = {'content_type':self.template.get_content_type_model,
                'object_id':self.template.id,
                'body':'test test comments'}

        self.client.credentials()
        response = self.client.post(self.comment_create_url, data, format='json')
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
    
        self.assertFalse('body' in response.data )
        self.assertFalse('object_id' in response.data )
        self.assertFalse('id' in response.data )

    def create_comment_for_check(self):
        data = {'content_type':self.meme.get_content_type_model,
                'object_id':self.meme.id,
                'body':'test test comments'}

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token['access'])
        response = self.client.post(self.comment_create_url, data, format='json')
        self.comment_id = response.data['id']
        self.comment_update_url= reverse('comments:comment_update',kwargs={'id':self.comment_id})
        self.comment_delete_url= reverse('comments:comment_delete',kwargs={'id':self.comment_id})

        data = {'content_type':self.template.get_content_type_model,
                'object_id':self.template.id,
                'body':'test test comments'}


        response = self.client.post(self.comment_create_url, data, format='json')
        self.comment_id_for_template = response.data['id']
        self.comment_update_url_for_template= reverse('comments:comment_update',kwargs={'id':self.comment_id_for_template})
        self.comment_delete_url_for_template= reverse('comments:comment_delete',kwargs={'id':self.comment_id_for_template})


    def test_comment_update(self):
        self.create_comment_for_check()
        up_data ={'body':'hello guys'} 
        response = self.client.patch(self.comment_update_url, up_data, format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['body'],up_data['body'])
        self.assertEqual(response.data['id'],self.comment_id)
        self.assertEqual(response.data['object_id'],self.meme.id)

       
        response = self.client.patch(self.comment_update_url_for_template, up_data, format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response.data['body'],up_data['body'])
        self.assertEqual(response.data['id'], self.comment_id_for_template)
        self.assertEqual(response.data['object_id'],self.template.id)

    def test_comment_update_without_credentials(self):
        self.create_comment_for_check()
        self.client.credentials()
        up_data ={'body':'hello guys'} 
        response = self.client.patch(self.comment_update_url, up_data, format='json')
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
        self.assertFalse('body' in response.data)

       
        response = self.client.patch(self.comment_update_url_for_template, up_data, format='json')
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
        self.assertFalse('body' in response.data)
    
    def test_comment_delete(self):
        self.create_comment_for_check()
      
        response = self.client.delete(self.comment_delete_url)
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertFalse(Comment.objects.filter(id=self.comment_id).exists())


       
        response = self.client.delete(self.comment_delete_url_for_template )

        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertFalse(Comment.objects.filter(id=self.comment_id).exists())


    def test_comment_delete_without_credentials(self):
        self.create_comment_for_check()
        self.client.credentials()
        response = self.client.delete(self.comment_delete_url)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Comment.objects.filter(id=self.comment_id).exists())

        response = self.client.delete(self.comment_delete_url_for_template)
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
        self.assertTrue(Comment.objects.filter(id=self.comment_id).exists())
    
        


    