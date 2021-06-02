
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase,APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model
User = get_user_model()
from django.conf import settings
from django.test import override_settings
from activities.models import Activity
from django.contrib.contenttypes.models import ContentType
from PIL import Image
import tempfile
import shutil
from netizen.models import Meme

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

@override_settings(MEDIA_ROOT=(settings.TEST_MEDIA_ROOT))
class ActivityTests(APITestCase):
        like_url= reverse('activities:like')
        bookmark_url = reverse('activities:bookmark')

        def setUp(self):
                self.user = User.objects.create(email='test2@2.com',username='testusername')
                self.user.set_password('testpassword123')
                self.user.save()
                self.token = get_tokens_for_user(self.user)
               
                self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token['access'])

                image = Image.new('RGB', (100, 100))
                self.tmp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
                image.save(self.tmp_file)
                self.tmp_file.seek(0)
                self.test_description =  'description teste tstttfvgs'

                meme_create_url = reverse('netizen:meme_upload')
                data = {'images':self.tmp_file,'description':self.test_description}
              

                response = self.client.post(meme_create_url, data, format='multipart')
        
                self.meme_id = response.data['id']
                self.meme =Meme.objects.get(id=self.meme_id)
                self.content_type = ContentType.objects.get(model=self.meme.get_content_type_model)


        def test_like(self):
                data={'content_type':self.content_type.model,      
                        'object_id':self.meme_id}
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
                data={'content_type':self.content_type.model,      
                        'object_id':self.meme_id}
                response = self.client.post(self.like_url, data, format='json')         # for like meme
                self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
                
                self.assertFalse(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.LIKE,user=self.user).exists())
                self.assertEqual(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.LIKE).count(),0)


                response = self.client.post(self.like_url, data, format='json')         # for unlike meme
                self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
        
                self.assertFalse(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.LIKE,user=self.user).exists())
                self.assertEqual(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.LIKE).count(),0)

        def test_bookmark(self):
                data={'content_type':self.content_type.model,      
                        'object_id':self.meme_id}
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
                data={'content_type':self.content_type.model,      
                        'object_id':self.meme_id}
                response = self.client.post(self.bookmark_url, data, format='json')         # for like meme
                self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
                
                self.assertFalse(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.BOOKMARK,user=self.user).exists())
                self.assertEqual(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.BOOKMARK).count(),0)


                response = self.client.post(self.bookmark_url, data, format='json')         # for unlike meme
                self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
        
                self.assertFalse(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.BOOKMARK,user=self.user).exists())
                self.assertEqual(Activity.objects.filter(content_type=self.meme.get_content_type,object_id=self.meme.id,activity_type=Activity.BOOKMARK).count(),0)



def tearDownModule():
    print ("\n Activities: Deleting temporary files...\n")
    try:
        shutil.rmtree(settings.TEST_MEDIA_ROOT)
    except OSError:
        pass