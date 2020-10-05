
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase,APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import get_user_model
User = get_user_model()

from reports.models import ContentReport,UserReport
from django.contrib.contenttypes.models import ContentType
from PIL import Image
import tempfile

from netizen.models import Meme

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class ContentReportTests(APITestCase):
        report_content_url= reverse('reports:report_content')
      

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
        
        def test_report_create(self):
            data={'content_type':self.meme.get_content_type_model,
                    'object_id':self.meme.id,
                    'subject':'first report'}

            response = self.client.post(self.report_content_url, data, format='json')   
            self.assertEqual(response.status_code,status.HTTP_200_OK)  

    
        
        def test_report_create_without_credentials(self):
            data={'content_type':self.meme.get_content_type_model,
                  'object_id':self.meme.id,
                    'description':'first report'}
            self.client.credentials()
            response = self.client.post(self.report_content_url, data, format='json')   
            self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)  



class UserReportTests(APITestCase):
        report_user_url = reverse('reports:report_user')
        
        def setUp(self):
            self.user = User.objects.create(email='test2@2.com',username='testusername')
            self.user.set_password('testpassword123')
            self.user.save()

            self.token = get_tokens_for_user(self.user)

            self.user2 = User.objects.create(email='test2@6.com',username='testusername78')
            self.user2.set_password('testpassword123')
            self.user2.save()

            self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token['access'])

        def test_user_report_create(self):
            data={'another_user_id':self.user2.id,
                    'subject':'report',
                    'description':'first report'}

            response = self.client.post(self.report_user_url, data, format='json')   
            self.assertEqual(response.status_code,status.HTTP_200_OK)  



        def test_user_report_create_without_credentials(self):
            data={'another_user':self.user2.id,
                    'subject':'report',
                    'description':'first report'}
            self.client.credentials()
            response = self.client.post(self.report_user_url, data, format='json')   
            self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)  