from django.shortcuts import render

from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import mixins
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from mysite.drf_defaults import DefaultResultsSetPagination
from django.contrib.contenttypes.models import ContentType
from .models import Template,Meme
from django.contrib.auth import get_user_model
User = get_user_model()
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.shortcuts import get_object_or_404
from django.http import Http404
from activities.helpers import mention
from .serializers import( TemplateListSerializer,
                            TemplateUploadSerializer,
                            MemeListSerializer,
                            MemeUploadSerializer,
                            TemplateDetailSerializer,
                            TemplatePatchSerializer,
                            MemeDetailSerializer,
                            MemePatchSerializer,
                            # UserMemeSerializer,
                            # UserTemplateSerializer,
                            ImageSerializer

                            )

class TemplatesList(generics.ListAPIView):
   

    # queryset = Template.objects.all()
    serializer_class = TemplateListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
            """
            Optionally restricts the returned qs to a given user,
            by filtering against a `username` query parameter in the URL.
            """
            queryset = Meme.objects.all()
            username = self.request.query_params.get('username')
            if username is not None:
                queryset = queryset.filter(user__username=username)
        
            return queryset


def upload_images(content_type,object_id,image):
    modified_data ={'image':image}
    file_serializer2 = ImageSerializer(data=modified_data)
    if file_serializer2.is_valid():
        file_serializer2.save(content_type=content_type,object_id=object_id)
        return file_serializer2.data , status.HTTP_201_CREATED
    else:
        return file_serializer2.errors , status.HTTP_400_BAD_REQUEST
   

class TemplateUploadView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        if 'images' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        data = {}
    
        user = get_object_or_404(User, id=request.user.id)
        file_serializer = TemplateUploadSerializer(data= request.data)
        
        if file_serializer.is_valid():
            template = file_serializer.save(user = user)
            # print(file_serializer)
            data['id'] = template.id
            data['username'] = template.user.username
            # data['images'] = template.images.url
            data['description'] = template.description

            images = dict((request.data).lists())['images']
            for image in images:
                res, stat = upload_images(content_type=template.get_content_type,object_id=template.id,image=image)
                if stat == status.HTTP_400_BAD_REQUEST:
                    template.delete()
                    return Response(res, status=status.HTTP_400_BAD_REQUEST)
                    
            mention(ContentType.objects.get_for_model(Template).model,data['id'],user,data['description'])
            return Response(data, status=status.HTTP_201_CREATED)
        else:
            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TemplateView(APIView):
    permission_classes = [IsAuthenticated]
    """
    Retrieve, update or delete a Template instance.
    """
    def get_object(self, id):
        try:
            return Template.objects.get(id=id)
        except Template.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        template = self.get_object(id)
        # print(template.id)
        serializer = TemplateDetailSerializer(template,context={'request': request })
        return Response(serializer.data)

    def patch(self, request, id, format=None):
        template = self.get_object(id)
        if template.user != request.user:
            return Response({'response':"You dont have permission to edit"},status = status.HTTP_403_FORBIDDEN)
        serializer = TemplatePatchSerializer(template, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        template = self.get_object(id)
        if template.user != request.user:
            return Response({'response':"You dont have permission to delete"},status = status.HTTP_403_FORBIDDEN)
        template.delete()
        data = {}
        data['response'] = "Deleted Succesfully"
        return Response(data,status=status.HTTP_200_OK)





class MemesList(generics.ListAPIView):
  

    # queryset = Meme.objects.all()
    serializer_class = MemeListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given user,
        by filtering against a `username` query parameter in the URL.
        """
        queryset = Meme.objects.all()
        username = self.request.query_params.get('username')
        if username is not None:
            queryset = queryset.filter(user__username=username)
    
        return queryset


# class UserMemesList(generics.ListAPIView):
   
#     serializer_class = UserMemeSerializer
#     permission_classes = [IsAuthenticated]
#     pagination_class = PageNumberPagination

#     def get_queryset(self):

#         username = self.kwargs['username']
#         user =  get_object_or_404(User, username=username)
#         return Meme.objects.filter(user=user)

# class UserTemplatesList(generics.ListAPIView):

#     serializer_class = UserTemplateSerializer
#     permission_classes = [IsAuthenticated]
#     pagination_class = PageNumberPagination

#     def get_queryset(self):

#         username = self.kwargs['username']
#         user =  get_object_or_404(User, username=username)
#         return Template.objects.filter(user=user)




class MemeUploadView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        if 'images' not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        data = {}
        user = get_object_or_404(User, id=request.user.id)
        

        file_serializer = MemeUploadSerializer(data=request.data)
        
        if file_serializer.is_valid():
            meme = file_serializer.save(user = user)
            data['id'] = meme.id
            data['username'] = meme.user.username
            # data['images'] = meme.images.url
            data['description'] = meme.description

            images = dict((request.data).lists())['images']
            for image in images:
                res,stat=upload_images(content_type=meme.get_content_type,object_id=meme.id,image=image)
                if stat == status.HTTP_400_BAD_REQUEST:
                    meme.delete()
                    return Response(res, status=status.HTTP_400_BAD_REQUEST)

            mention(ContentType.objects.get_for_model(Meme).model,data['id'],user,data['description'])
            return Response(data, status=status.HTTP_201_CREATED)
        else:

            return Response(file_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MemeView(APIView):
    permission_classes = [IsAuthenticated]
    """
    Retrieve, update or delete a Template instance.
    """
    def get_object(self, id):
        try:
            return Meme.objects.get(id=id)
        except Meme.DoesNotExist:
            raise Http404

    def get(self, request, id, format=None):
        meme = self.get_object(id)
        serializer = MemeDetailSerializer(meme,context={'request': request })
        
        # print(request.META)
        return Response(serializer.data)

    def patch(self, request, id, format=None):
        meme = self.get_object(id)
        if meme.user != request.user:
            return Response({'response':"You dont have permission to edit"},status = status.HTTP_403_FORBIDDEN)
        serializer = MemePatchSerializer(meme, data=request.data,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id, format=None):
        meme = self.get_object(id)
       
        if meme.user != request.user:
            return Response({'response':"You dont have permission to delete"},status = status.HTTP_403_FORBIDDEN)
        meme.delete()
        data = {}
        data['response'] = "Deleted Succesfully"
        return Response(data,status=status.HTTP_200_OK)            



