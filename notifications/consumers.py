import json
from channels.generic.websocket import AsyncWebsocketConsumer


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']

        if self.user.is_authenticated:
            await self.accept()
            await self.channel_layer.group_add(self.user.username, self.channel_name)
            await self.channel_layer.group_add("all-users", self.channel_name)
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.user.username, self.channel_name)
        await self.channel_layer.group_discard("all-users", self.channel_name)

    async def send_notification(self, event):

        # Send the notification to the user
        await self.send(text_data=json.dumps({"type": "notification"}))
