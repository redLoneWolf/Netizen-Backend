from datetime import date
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase,APIClient
import json
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework_simplejwt.tokens import RefreshToken
from django.core import mail
from jwt import decode as jwt_decode

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class AccountTests(APITestCase):
    register_url = reverse('accounts:register')

    login_url = reverse('accounts:token_obtain_pair')

    

    def test_create_account(self):
        """
        Ensure we can create a new account object.
        """
        
        data = {'email': 'test@test.com','email2':'test@test.com','username':'TestUsername','password':'testpassword123','password2':'testpassword123'}

        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # self.assertTrue('id' in response.data )
        # self.assertEqual(response.data['username'], data['username'])
        # self.assertTrue(response.data['token'])
        decoded = jwt_decode(response.data['access'],settings.SECRET_KEY, algorithms=["HS256"])
        user = User.objects.get(id=decoded['user_id'])
        self.assertTrue(user.is_active)

    def test_account_login(self):
        password='testpassword001'
        username='testusername'
        email='test@test.com'
        user = User.objects.create(email=email,username=username)
        user.set_password(password)
        user.save()

        

        data1={"email":user.email,"password":password}

        response = self.client.post(self.login_url, data1,format='json')
 
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.assertTrue(response.data['access'])
        self.assertTrue(response.data['refresh'])
    
    def test_for_similar_account(self):
        password='testpassword001'
        username='testusername'
        email='test@test.com'
        user = User.objects.create(email=email,username=username)
        user.set_password(password)
        user.save()

        user2 = {'email':email,'username':'TestUsername','password':'testpassword123','password2':'testpassword123'}
        response = self.client.post(self.register_url, user2, format='json')
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)

        user3 = {'email':'test2@test2.com','username':username,'password':'testpassword123','password2':'testpassword123'}
        response2 = self.client.post(self.register_url, user3, format='json')
        self.assertEqual(response2.status_code,status.HTTP_400_BAD_REQUEST)

        user4 = {'email':'test3@test.com','username':'test_username','password':'testpassword13','password2':'testpassword123'}
        response2 = self.client.post(self.register_url, user4, format='json')
        self.assertEqual(response2.status_code,status.HTTP_400_BAD_REQUEST)



class PasswordChangeTests(APITestCase):
    token =None
    email = 'test@test.com'
    username = 'testusername'
    password = 'testpassword'

    new_password = 'testpassword2456'

    change_password_url =reverse('accounts:change_password')
    
    user = None

    def setUp(self):
        self.user = User.objects.create(email=self.email,username=self.username)
        self.user.set_password(self.password)
        self.user.save()
        self.token = get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token['access'])
        

    def test_password_changed(self):

        data = {'old_password':self.password,'new_password':self.new_password,'new_password2':self.new_password}

        response = self.client.post(self.change_password_url, data, format='json')

        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.new_password))


    def test_password_change_for_non_matching_password(self):

        data = {'old_password':self.password,'new_password':self.new_password,'new_password2':'newwrongpassword'}

        response = self.client.post(self.change_password_url, data, format='json')
 
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(self.new_password))
        self.assertTrue(self.user.check_password(self.password))

    def test_password_change_for_wrong_old_password(self):
    
        data = {'old_password':'wrongpassword001','new_password':self.new_password,'new_password2':self.new_password}

        response = self.client.post(self.change_password_url, data, format='json')
 
        self.assertEqual(response.status_code,status.HTTP_400_BAD_REQUEST)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(self.new_password))
        self.assertTrue(self.user.check_password(self.password))

    def test_password_change_without_credentials(self):
   
        self.client.credentials()
        data = {'old_password':self.password,'new_password':self.new_password,'new_password2':self.new_password}

        response = self.client.post(self.change_password_url, data, format='json')
     
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
        self.user.refresh_from_db()
        self.assertFalse(self.user.check_password(self.new_password))
        self.assertTrue(self.user.check_password(self.password))

class UserListAndDetailAccessTests(APITestCase):
    token =None
    email = 'test@test.com'
    username = 'testusername'
    password = 'testpassword'
    users_list_url = reverse('accounts:users_list')
    users_detail_url = reverse('accounts:users_list')
   
    user = None

    def setUp(self):
        self.user = User.objects.create(email=self.email,username=self.username)
        self.user.set_password(self.password)
        self.user.save()
        self.token = get_tokens_for_user(self.user)
        

    def test_access(self):
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token['access'])
        response = self.client.get(self.users_list_url, format='json')
        response2 = self.client.get(self.users_detail_url, format='json')
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(response2.status_code,status.HTTP_200_OK)
    
    def test_no_access(self):
       
        self.client.credentials()
        response = self.client.get(self.users_list_url, format='json')
        response2 = self.client.get(self.users_detail_url, format='json')
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response2.status_code,status.HTTP_401_UNAUTHORIZED)










class PasswordResetTests(APITestCase):


   
    reset_password_url = reverse('accounts:password_reset')

    def setUp(self):
        self.user = User.objects.create(email='test@2.com',username='testusername')
        self.user.set_password('testpassword')
        self.user.save()
        data={'email':'test@2.com'}
        self.response = self.client.post(self.reset_password_url, data, format='json')
        self.mail = mail.outbox[0]


    def test_sent_mail(self):
        self.assertEqual(self.response.status_code,status.HTTP_200_OK)
       

        

    def test_email_subject(self):
        self.assertEqual('Please reset your password', self.mail.subject)

    def test_email_body(self):
        context = self.response.context
        token = context.get('token')
        uid = context.get('uid')
        password_reset_token_url = reverse('accounts:password_reset_confirm', kwargs={
            'uidb64': uid,
            'token': token
        })
        self.assertIn(password_reset_token_url, self.mail.body)
        self.assertIn(self.user.username, self.mail.body)
        self.assertIn(self.user.email, self.mail.body)

    def test_email_to(self):
        self.assertEqual([self.user.email,], self.mail.to)


class UserUpdateTest(APITestCase):
    token =None
    email = 'test@test.com'
    username = 'testusername'
    password = 'testpassword'
    url = reverse('accounts:profile')
    
   
    user = None

    def setUp(self):
        self.user = User.objects.create(email=self.email,username=self.username)
        self.user.set_password(self.password)
        self.user.save()
        self.token = get_tokens_for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token['access'])

    def test_username_and_about_change(self):
        data={'username':"newusername"} 
        response = self.client.patch(self.url, data, format='json')      #username only
        
        self.assertEqual(response.data['username'],data['username'])

        data={'about':"new about"} 
        response = self.client.patch(self.url, data, format='json')      #about only
        
        self.assertEqual(response.data['about'],data['about'])

        data={'username':"newusername",'about':"new about"} 
        response = self.client.patch(self.url, data, format='json')      #about only

        self.assertEqual(response.data['username'],data['username'])
        self.assertEqual(response.data['about'],data['about'])
   
    def test_username_and_about_change_without_credentials(self):
        self.client.credentials()
        data={'username':"newusername"} 
        response = self.client.patch(self.url, data, format='json')      #username only
        
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

        data={'about':"new about"} 
        response = self.client.patch(self.url, data, format='json')      #about only
        
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)

        data={'username':"newusername",'about':"new about"} 
        response = self.client.patch(self.url, data, format='json')      #about only
        
        self.assertEqual(response.status_code,status.HTTP_401_UNAUTHORIZED)
        