from django.db import close_old_connections
from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode
from django.conf import settings
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
from channels.db import database_sync_to_async
import asyncio
from channels.auth import AuthMiddlewareStack
@database_sync_to_async
def close_connections():
    close_old_connections()

@database_sync_to_async
def get_user(user_jwt):
    try:
        # print(User.objects.get(id=user_jwt).id)
        return get_user_model().objects.get(id=user_jwt)
        # get_user_model().objects.get(id=decoded_data["user_id"])
    except get_user_model().DoesNotExist:
        return InvalidToken



class TokenAuthMiddleware:
    """
    Custom token auth middleware
    """

    def __init__(self, inner):
        # Store the ASGI application we were passed
        self.inner = inner

    def __call__(self, scope):
        return TokenAuthMiddlewareInstance(scope, self)
       
        
class TokenAuthMiddlewareInstance:
    def __init__(self, scope, middleware):
        self.middleware = middleware
        self.scope = dict(scope)
        self.inner = self.middleware.inner
    
    async def __call__(self, receive, send):
        await close_connections()
        # Get the token
        token = parse_qs(self.scope["query_string"].decode("utf8"))["token"][0]

        # Try to authenticate the user
        try:
            # This will automatically validate the token and raise an error if token is invalid
            UntypedToken(token)
        except (InvalidToken, TokenError) as e:
            # Token is invalid
            print(e)
            return None
        else:
            #  Then token is valid, decode it
            decoded_data = jwt_decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            # print(decoded_data)
            # Will return a dictionary like -
            # {
            #     "token_type": "access",
            #     "exp": 1568770772,
            #     "jti": "5c15e80d65b04c20ad34d77b6703251b",
            #     "user_id": 6
            # }

            # Get the user using ID
            # user = await get_user(decoded_data['user_id'])
            self.scope['user'] = await get_user(decoded_data['user_id'])
            # print(self.scope['user'].email)
            inner = self.inner(self.scope)
            # return self.inner(dict(scope,user))
            return await inner(receive, send) 
            

        # Return the inner application directly and let it run everything else
        
# TokenAuthMiddlewareStack = lambda inner: TokenAuthMiddleware(AuthMiddlewareStack(inner))
