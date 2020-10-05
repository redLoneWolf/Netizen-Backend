from django.urls import path
from channels.routing import ProtocolTypeRouter,URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator,OriginValidator

from chats.consumers import ChatConsumer
from .jwt_token_auth_middleware import TokenAuthMiddleware

application = ProtocolTypeRouter({
    # Empty for now (http->django views is added by default)

    'websocket':TokenAuthMiddleware (
        
            URLRouter(
                [
                        path("chats/<str:username>",ChatConsumer),
                ]   
            )
        
    )
    
})