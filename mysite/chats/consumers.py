import asyncio
import json
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from channels.exceptions import StopConsumer
from .models import Room,Message
from django.contrib.auth import get_user_model
User = get_user_model()
from channels.generic.websocket import AsyncWebsocketConsumer
class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        other_user = self.scope['url_route']['kwargs']['username']
        me = self.scope['user']
        room = await self.get_room(me,other_user)
        self.room_obj =room
        chat_room = f"room_{room.id}"
        self.chat_room = chat_room
        await self.channel_layer.group_add(
             self.chat_room,
            self.channel_name
        )
        await self.accept()

   


        

    async def receive(self,text_data):
        print('received',text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

      
        user = self.scope['user']
      
        if user.is_authenticated:
            username = user.username
                
  

          
        await self.create_message(user=user, msg=message)

        await self.channel_layer.group_send(
            self.chat_room,
            {
                "type":'chat_message',
                "message":message,
            
            }
        )
            

    async def chat_message(self,event):
        # print("message", event)
        message = event['message']
        # print(event)
        await self.send(text_data=json.dumps({'message': message}))

    async def disconnect(self,close_code):
        print('disconnected',close_code) 
        await self.channel_layer.group_discard(
            self.chat_room,
            self.channel_name
        )

    @database_sync_to_async
    def get_room(self,user,other_user):
        return Room.objects.get_or_create(user=user,other_username=other_user)[0]

    @database_sync_to_async
    def create_message(self,user,msg):
        # user = User.objects.get(username='a')
        return Message.objects.create(user=user,thread=self.room_obj,message=msg)
