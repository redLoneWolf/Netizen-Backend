
from django.http.response import Http404, HttpResponseBadRequest
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from rest_framework import generics
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
User = get_user_model()
from django.shortcuts import get_object_or_404
from .models import Comment
from.serializers import CommentCreateSerializer,CommentSerializer
from activities.helpers import mention

class CommentList(generics.ListAPIView):
    """
    API endpoint that allows users to be viewed or edited.
    """

    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    

    def get_queryset(self):
        # print(self.kwargs)
        content_type_model = self.request.query_params.get('content_type', None)
        
        content_type = get_object_or_404(ContentType,model=content_type_model)
        
        object_id = self.request.query_params.get('object_id', None)
        parent_id = self.request.query_params.get('parent_id', None)

        if object_id is None or content_type_model is None:
            raise Http404

        try:
            post = content_type.get_object_for_this_type(id=object_id)
        except ObjectDoesNotExist:
            raise Http404

        if parent_id:
            parent = get_object_or_404(Comment,id=parent_id,object_id=post.id)

            return Comment.objects.filter(object_id = post.id,content_type_id=content_type.id,parent_id=parent.id)
        else:
            parent = None
            return Comment.objects.filter(object_id = post.id,content_type_id=content_type.id,parent_id=None)
      


        

class CommentCreateView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):

        if not ('content_type' in  request.data and 'object_id' in request.data) :
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
        content_type_model = request.data['content_type']
        object_id = request.data['object_id']

        try:
            content_type = ContentType.objects.get(model=content_type_model)
        except ContentType.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            post = content_type.get_object_for_this_type(id=object_id)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)


        user = get_object_or_404(User,id=request.user.id)


        serializer = CommentCreateSerializer(data=request.data)
     
        if serializer.is_valid():
            parent_obj = None
            try:
                parent_id = request.data['parent_id']
            except:
                parent_id = None
            
            if parent_id:
                parent_obj = Comment.objects.get(id=parent_id)
                
                if parent_obj:

                    serializer.save(parent = parent_obj,user=user,content_type = content_type,object_id = post.id)
                    
                    mention(ContentType.objects.get_for_model(Comment).model,serializer.data['id'],user,serializer.data['body'])
                    return Response(serializer.data, status=status.HTTP_200_OK)
            
            
            serializer.save(user=user,content_type = content_type,object_id = post.id)
         
            mention(ContentType.objects.get_for_model(Comment).model,serializer.data['id'],user,serializer.data['body'])
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CommentDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, id):
       
        return get_object_or_404(Comment,id=id)
        

    def delete(self, request, id, format=None):
        comment = self.get_object(id)
       
        if comment.user != request.user:
            return Response({'response':"You dont have permission to delete"},status = status.HTTP_403_FORBIDDEN)
        comment.delete()
        data = {}
        data['response'] = "Deleted Succesfully"
        return Response(data,status=status.HTTP_200_OK) 

class CommentUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, id):
        return get_object_or_404(Comment,id=id)
        
    def patch(self, request, id, format=None):
        comment = self.get_object(id)
        if comment.user != request.user:
            return Response({'response':"You dont have permission to edit"},status = status.HTTP_403_FORBIDDEN)
        serializer = CommentCreateSerializer(comment, data=request.data,partial=True)
        data={}
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

      
            

            

