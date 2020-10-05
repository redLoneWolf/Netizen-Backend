
from django.contrib.auth import get_user_model

User = get_user_model()


from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from .serializers import UserSerializer,RegistrationSerializer,PasswordSerializer,UserUpdateSerializer,UserQuerSerializer
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.authtoken.models import Token
from django.contrib.auth import password_validation
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.contrib.sites.shortcuts import get_current_site
from django.template import loader
from django.utils.encoding import force_bytes
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .forms import SetPasswordForm
from django.utils.translation import gettext_lazy as _
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from django.core.exceptions import ValidationError
from django.utils.http import  urlsafe_base64_decode
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
INTERNAL_RESET_SESSION_TOKEN = '_password_reset_token'
from rest_framework.pagination import PageNumberPagination
from django.conf import settings

from google.auth.transport import requests as google_transport_requests
from google.oauth2 import id_token

from rest_framework_simplejwt.tokens import RefreshToken

from django.views.generic.base import TemplateView
from activities.helpers import update
from rest_framework import filters
from relationships.helpers import get_blockers,get_blocked_users
class UserCreateAPIView(APIView):
	permission_classes = [AllowAny]
	def post(self, request):
		if request.method == 'POST':
			data = {}


			serializer = RegistrationSerializer(data=request.data)
			
			if serializer.is_valid(raise_exception=True):
				user = serializer.save()
			
				token = get_tokens_for_user(user)

				return Response(token,status=status.HTTP_201_CREATED)
			else:
				data = serializer.errors
			return Response(data,status.HTTP_400_BAD_REQUEST)





class PasswordChangeView(APIView):
	permission_classes = [IsAuthenticated]

	def post(self, request, *args, **kwargs):
		current_user = User.objects.get(id=request.user.id)
		serializer = PasswordSerializer(data=request.data)
		if serializer.is_valid():
			# print(serializer.validated_data["new_password"])
			if not current_user.check_password(serializer.validated_data.get("old_password")):
				return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
			new_password = serializer.validated_data.get("new_password")
			new_password2 = serializer.validated_data.get("new_password2")

			if new_password != new_password2:
				return Response({"new_password": ["New passwords must match"]}, status=status.HTTP_400_BAD_REQUEST)

			try:
				password_validation.validate_password(serializer.validated_data.get('new_password'),current_user)
				password_validation.validate_password(serializer.validated_data.get('new_password2'),current_user)
			except ValidationError as e :
				# print(e)
				return Response({"new_password": e.messages}, status=status.HTTP_400_BAD_REQUEST)
			

			current_user.set_password(new_password2)
			current_user.save()
			
			return Response({'response':"password changed successfully"}, status=status.HTTP_200_OK)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserListView(generics.ListAPIView):
	permission_classes = [IsAuthenticated]
	filter_backends = [filters.SearchFilter]
	search_fields = ['^username']
	queryset = User.objects.all()
	pagination_class = PageNumberPagination
	pagination_class.page_size = 2
	serializer_class = UserQuerSerializer

	def list(self, request, *args, **kwargs):
		queryset = self.filter_queryset(self.get_queryset())

		queryset = queryset.exclude(id__in=get_blockers(request.user))


		page = self.paginate_queryset(queryset)
		if page is not None:
			serializer = self.get_serializer(page, many=True)
			return self.get_paginated_response(serializer.data)

		serializer = self.get_serializer(queryset, many=True)
		return Response(serializer.data)
	


class UserDetailView(APIView):
	permission_classes = [IsAuthenticated]
	
	def get(self, request,username, format=None):
		qs = User.objects.all()
		user = get_object_or_404(qs, username=username)
		serializer = UserSerializer(user,context={'request': request })
		return Response(serializer.data)

class MyProfileView(APIView):
	permission_classes = [IsAuthenticated]
	
	def get(self, request, format=None):
		qs = User.objects.all()
		user = get_object_or_404(qs, id= request.user.id,username=request.user.username)
		serializer = UserSerializer(user,context={'request': request})
		# print(user.followers)
		return Response(serializer.data)

	def patch(self, request, *args, **kwargs):
		current_user = User.objects.get(id=request.user.id)
		serializer = UserUpdateSerializer(current_user,data=request.data,partial=True)

		if serializer.is_valid():
			if 'username' in request.data:
				update(request.user.username,request.data['username'])

			serializer.save()
			return Response(serializer.data, status=status.HTTP_200_OK)
		else:
			return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
	

	def delete(self, request, *args, **kwargs):

		current_user = User.objects.get(id=request.user.id)
		current_user.delete()

		return Response(status=status.HTTP_204_NO_CONTENT)

class PasswordResetView(APIView):
	permission_classes = [AllowAny]
	def post(self, request, *args, **kwargs):
		use_https = False
		email_template_name = 'password_reset_email.html'
		html_email_template_name = 'password_reset_email_template.html'
		subject_template_name = 'password_reset_subject.txt'
		from_email = None
		token_generator = default_token_generator

		if 'email' not in request.data:
			return  Response({'response':'error'}, status=status.HTTP_400_BAD_REQUEST)


		user_email = request.data['email']
		user =  get_object_or_404(User, email=user_email)
		current_site = get_current_site(request)
		site_name = current_site.name
		domain = current_site.domain
		context = {
			'email': user_email,
			'domain': domain,
			'site_name': site_name,
			'uid': urlsafe_base64_encode(force_bytes(user.pk)),
			'user': user,
			'token': token_generator.make_token(user),
			'protocol': 'https' if use_https else 'http',
			
		}
		self.send_mail(subject_template_name,email_template_name, context, from_email,user_email, html_email_template_name=html_email_template_name,)
		return  Response({'email':"email sent successfully"}, status=status.HTTP_200_OK)

	def send_mail(self, subject_template_name,email_template_name,
				context, from_email, to_email, html_email_template_name=None):

		subject = loader.render_to_string(subject_template_name, context)
		# Email subject *must not* contain newlines
		subject = ''.join(subject.splitlines())
		body = loader.render_to_string(email_template_name, context)
	   
		html_email = loader.render_to_string(html_email_template_name, context)
		email_message = EmailMultiAlternatives(subject, html_email, from_email, [to_email])
	
	


		email_message.send()


class PasswordResetConfirmView( FormView):
    form_class = SetPasswordForm
    post_reset_login = False
    post_reset_login_backend = None
    reset_url_token = 'set-password'
    success_url = reverse_lazy('accounts:password_reset_complete')
    template_name = 'password_reset_confirm.html'
    title = _('Enter new password')
    token_generator = default_token_generator

    @method_decorator(sensitive_post_parameters())
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        assert 'uidb64' in kwargs and 'token' in kwargs

        self.validlink = False
        self.user = self.get_user(kwargs['uidb64'])

        if self.user is not None:
            token = kwargs['token']
            if token == self.reset_url_token:
                session_token = self.request.session.get(INTERNAL_RESET_SESSION_TOKEN)
                if self.token_generator.check_token(self.user, session_token):
                    # If the token is valid, display the password reset form.
                    self.validlink = True
                    return super().dispatch(*args, **kwargs)
            else:
                if self.token_generator.check_token(self.user, token):
                    # Store the token in the session and redirect to the
                    # password reset form at a URL without the token. That
                    # avoids the possibility of leaking the token in the
                    # HTTP Referer header.
                    self.request.session[INTERNAL_RESET_SESSION_TOKEN] = token
                    redirect_url = self.request.path.replace(token, self.reset_url_token)
                    return HttpResponseRedirect(redirect_url)

        # Display the "Password reset unsuccessful" page.
        return self.render_to_response(self.get_context_data())

    def get_user(self, uidb64):
        try:
            # urlsafe_base64_decode() decodes to bytestring
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist, ValidationError):
            user = None
        return user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        del self.request.session[INTERNAL_RESET_SESSION_TOKEN]
        # if self.post_reset_login:
			
			# auth_login(self.request, user, self.post_reset_login_backend)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.validlink:
            context['validlink'] = True
        else:
            context.update({
                'form': None,
                'title': _('Password reset unsuccessful'),
                'validlink': False,
            })
        return context


class PasswordResetDoneView(TemplateView):
    template_name = 'password_reset_complete.html'
    title = _('Password reset sent')

class GoogleLoginDoneView(TemplateView):
    template_name = 'login.html'
    title = _('Password reset sent')

class GoogleRegisterView(APIView):
	permission_classes = [AllowAny]
	def post(self, request, *args, **kwargs):
		client_id = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
		idinfo = id_token.verify_oauth2_token(request.data['code'], google_transport_requests.Request(), client_id)
		# print(idinfo)

		if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
			raise ValueError('Wrong issuer.')
		
		data={}
		data['username'] = request.data['username']
		data['email'] = idinfo['email']
		data['email2'] = idinfo['email']
		data['password'] = request.data['password']
		data['password2'] = request.data['password2']
		
		serializer = RegistrationSerializer(data=data)
		
		if serializer.is_valid():
			user = serializer.save()
			token = get_tokens_for_user(user)
			response={}
			response['response'] = 'successfully registered new user.'
			response['id'] = user.id
			response['username'] = user.username
			
			response['token'] = token
		else:
			response = serializer.errors
		return Response(response)



class GoogleLoginView(APIView):
	permission_classes = [AllowAny]
	def post(self, request, *args, **kwargs):
		client_id = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
		idinfo = id_token.verify_oauth2_token(request.data['code'], google_transport_requests.Request(), client_id)


		if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
			raise ValueError('Wrong issuer.')

		try:
			user = User.objects.get(email=idinfo['email'])
			if not user:
				return Response({'error': 'Auth failed'}, status=status.HTTP_401_UNAUTHORIZED)
			token = get_tokens_for_user(user)

			return Response(token, status=status.HTTP_200_OK)
		except Exception as ex:
			return Response({'error': str(ex)}, status=status.HTTP_401_UNAUTHORIZED)



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }



