from django.test import TestCase

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase,APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
User = get_user_model()

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class FollowTest(APITestCase):
    token =None
    follow_url = reverse('relationships:follow')
 
    user1 = None
    user2 = None
    token1 = None
    token2=None

    def setUp(self):
        self.user1 = User.objects.create(email='email@user1.com',username='usernameof1')
        self.user1.set_password('passwordof1')
        self.user1.save()
        self.token1 = get_tokens_for_user(self.user1)

        self.user2 = User.objects.create(email='email@user2.com',username='usernameof2')
        self.user2.set_password('passwordof2')
        self.user2.save()
        self.token2 = get_tokens_for_user(self.user2)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token1['access'])
    
    def test_follow(self):

        data={'to_follow':self.user2.username} 
        response = self.client.post(self.follow_url, data, format='json')       # first post for follow
     
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(self.user1.following.count(), 1 )

        self.assertTrue(self.user1.following.filter(followee=self.user2).exists())
        self.assertTrue(self.user2.followers.filter(follower=self.user1).exists())
    
 
        data={'to_follow':self.user2.username} 
        response = self.client.post(self.follow_url, data, format='json')       # second post for unfollow
     
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(self.user1.following.count(), 0 )

        self.assertFalse(self.user1.following.filter(followee=self.user2).exists())
        self.assertFalse(self.user2.followers.filter(follower=self.user1).exists())

class BlockTest(APITestCase):
    token =None
    follow_url = reverse('relationships:block')
 
    user1 = None
    user2 = None
    token1 = None
    token2=None

    def setUp(self):
        self.user1 = User.objects.create(email='email@user1.com',username='usernameof1')
        self.user1.set_password('passwordof1')
        self.user1.save()
        self.token1 = get_tokens_for_user(self.user1)

        self.user2 = User.objects.create(email='email@user2.com',username='usernameof2')
        self.user2.set_password('passwordof2')
        self.user2.save()
        self.token2 = get_tokens_for_user(self.user2)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token1['access'])
    
    def test_follow(self):

        data={'user_to_block':self.user2.username} 
        response = self.client.post(self.follow_url, data, format='json')       # first post for follow
     
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(self.user1.blocking.count(), 1 )

        self.assertTrue(self.user1.blocking.filter(blocked=self.user2).exists())
        self.assertTrue(self.user2.blockees.filter(blocker=self.user1).exists())
    
 
        data={'user_to_block':self.user2.username} 
        response = self.client.post(self.follow_url, data, format='json')       # second post for unfollow
     
        self.assertEqual(response.status_code,status.HTTP_200_OK)
        self.assertEqual(self.user1.blocking.count(), 0 )

        self.assertFalse(self.user1.blocking.filter(blocked=self.user2).exists())
        self.assertFalse(self.user2.blockees.filter(blocker=self.user1).exists())