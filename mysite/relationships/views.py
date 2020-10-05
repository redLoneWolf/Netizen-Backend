from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated

from django.contrib.auth import get_user_model
User = get_user_model()
from .helpers import do_folllow,do_block
from rest_framework import status
from rest_framework.response import Response
from .models import Block
# Create your views here.
class FollowView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, *args, **kwargs):
		data = {}

		current_user = User.objects.get(id=request.user.id)
		
		username_of_user_to_follow = request.data['to_follow']

		user_to_follow = User.objects.get(username=username_of_user_to_follow)
		if current_user == user_to_follow:
    			return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
		# print(user_to_follow)
		is_following = do_folllow(current_user=current_user,user_to_follow=user_to_follow)
		
		data['is_following'] = is_following
		return Response(data, status=status.HTTP_200_OK)

class BlockView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, *args, **kwargs):
		data = {}

		current_user = User.objects.get(id=request.user.id)
		
		username_of_user_to_follow = request.data['user_to_block']

		user_to_block = User.objects.get(username=username_of_user_to_follow)
		if current_user == user_to_block:
    			return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
	
		is_blocked = do_block(blocker_user=current_user,blocked_user=user_to_block)
		# print(Block.objects.get_blocked_users(current_user))
		data['is_blocked'] = is_blocked
		return Response(data, status=status.HTTP_200_OK)