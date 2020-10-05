
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from django.contrib.contenttypes.models import ContentType
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.contrib.auth import get_user_model
User = get_user_model()
from .models import ContentReport,UserReport

class ContentReportCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):

        if ('content_type'not in request.data or 'object_id' not in request.data or 'subject' not in request.data ):
            return Response(status=status.HTTP_400_BAD_REQUEST)

        content_type_model = request.data['content_type']
        content_type = ContentType.objects.get(model=content_type_model)
        object_id = request.data['object_id']
        subject = request.data['subject']
        post = content_type.get_object_for_this_type(id=object_id)
        data={}

        user = get_object_or_404(User,id=request.user.id)
        if 'description' in request.data:
            description = request.data['description']
            ContentReport.objects.create(object_id=post.id,content_type=content_type,description=description,user=user,subject=subject)
        else:
            ContentReport.objects.create(object_id=post.id,content_type=content_type,user=user,subject=subject)
        data['response'] ="Reported Successfully"
        return Response(data, status=status.HTTP_200_OK)

class UserReportCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):

        if ('another_user_id'not in request.data or 'subject' not in request.data  ):
                return Response(status=status.HTTP_400_BAD_REQUEST)

        current_user = get_object_or_404(User,id=request.user.id)
        reported_user_id = request.data['another_user_id']
        reported_user = get_object_or_404(User,id=reported_user_id)
        subject = request.data['subject']
        
        if current_user == reported_user:
            return Response({'error':"Cannot Report Same User"},status=status.HTTP_400_BAD_REQUEST)

        if 'description' in request.data:
            description = request.data['description']
            UserReport.objects.create(user=reported_user,subject=subject,description=description,reporter=current_user)
        else:
            UserReport.objects.create(user=reported_user,subject=subject,reporter=current_user)

        data={}
        data['response'] ="Reported Successfully"
     
        return Response(data, status=status.HTTP_200_OK)