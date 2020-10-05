from .models import Activity

from django.contrib.auth import get_user_model
User = get_user_model()

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .helpers import do_like,do_bookmark,get_total_likes,get_total_favourites


class LikeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = {}
        # user = get_object_or_404(User, id=request.user.id)
        # print(request.user)
        user = User.objects.get(id=request.user.id)

        content_type_model = request.data['content_type']
        content_type = ContentType.objects.get(model=content_type_model)
        object_id = request.data['object_id']


        is_liked = do_like(content_type=content_type,
                           object_id=object_id, user=user)


        post = content_type.get_object_for_this_type(id=object_id)
        # print(get_total_likes(content_type_id,object_id))
        data['post'] = post.id
        data['is_liked'] = is_liked
        data['likes']  = get_total_likes(content_type.model,post.id)
        # data['likes']  = post.total_likes

        return Response(data, status=status.HTTP_200_OK)

class BookmarkView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        data = {}
        # user = get_object_or_404(User, id=request.user.id)
        # print(request.user)
        user = User.objects.get(id=request.user.id)

        content_type_model = request.data['content_type']
        content_type = ContentType.objects.get(model=content_type_model)
        object_id = request.data['object_id']


        is_bookmarked = do_bookmark(content_type=content_type,
                           object_id=object_id, user=user)


        post = content_type.get_object_for_this_type(id=object_id)
        # print(get_total_likes(content_type.model,object_id))
        data['post'] = post.id
        data['is_bookmarked'] = is_bookmarked
     
        # data['likes']  = post.total_likes

        return Response(data, status=status.HTTP_200_OK)


        