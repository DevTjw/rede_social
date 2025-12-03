import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Max, Prefetch


User = get_user_model()

class ChatRoomConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_anonymous:
            await self.close()
            return

        self.chat_box_name = self.scope['url_route']['kwargs']['chat_box_name']
        self.group_name = f'chat_{self.chat_box_name}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

        conversas = await self.get_conversas_nao_lidas(self.user)
        await self.send(text_data=json.dumps({
            'type': 'conversas_nao_lidas',
            'data': conversas,
        }))

    async def disconnect(self, close_code):
        if not self.user.is_anonymous:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        event_type = data.get('type', 'message')
        destinatario_username = data.get('destinatario')

        if not destinatario_username:
            return

        if event_type == 'message':
            message = data['message']
            destinatario_user = await self.get_user_by_username(destinatario_username)
            if not destinatario_user:
                return

            await self.save_message(self.user, destinatario_user, message)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'chatbox_message',
                    'message': message,
                    'remetente': self.user.username,
                    'destinatario': destinatario_username
                }
            )

        elif event_type == 'typing':
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'user_typing',
                    'remetente': self.user.username
                }
            )

        elif event_type == 'read':
            destinatario_user = await self.get_user_by_username(destinatario_username)
            if not destinatario_user:
                return

            await self.mark_as_read(self.user, destinatario_user)

            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'message_read',
                    'remetente': self.user.username
                }
            )

    # Eventos do grupo
    async def chatbox_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message'],
            'remetente': event['remetente'],
            'destinatario': event['destinatario']
        }))

    async def user_typing(self, event):
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'remetente': event['remetente']
        }))

    async def message_read(self, event):
        await self.send(text_data=json.dumps({
            'type': 'read',
            'remetente': event['remetente']
        }))

    @database_sync_to_async
    def get_user_by_username(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, remetente, destinatario, message):
        from .models import Mensagem
        return Mensagem.objects.create(
            remetente=remetente,
            destinatario=destinatario,
            conteudo=message
        )

    @database_sync_to_async
    def mark_as_read(self, remetente, destinatario):
        from .models import Mensagem
        Mensagem.objects.filter(
            remetente=destinatario,
            destinatario=remetente,
            lida=False
        ).update(lida=True)

    @database_sync_to_async
    def get_conversas_nao_lidas(self, user):
        # Importação local para evitar AppRegistryNotReady
        from usuarios.models import Perfil
        from .models import Mensagem  

        # Trazer todas mensagens relevantes agrupadas
        mensagens_agrupadas = (
            Mensagem.objects.filter(Q(destinatario=user) | Q(remetente=user))
            .values(
                "remetente__id", "remetente__username",
                "destinatario__id", "destinatario__username"
            )
            .annotate(
                total=Count("id"),
                nao_lidas=Count("id", filter=Q(lida=False, destinatario=user)),
                ultima_data=Max("data_envio")
            )
            .order_by("-ultima_data")
        )

        # Buscar todos os usuários e perfis de uma vez
        ids = set()
        for m in mensagens_agrupadas:
            ids.add(m["remetente__id"])
            ids.add(m["destinatario__id"])

        usuarios = User.objects.filter(id__in=ids).select_related("perfil")
        perfis_map = {u.id: u.perfil.foto_perfil.url if hasattr(u, "perfil") and u.perfil.foto_perfil else None for u in usuarios}

        conversas = {}
        for m in mensagens_agrupadas:
            if m["nao_lidas"] == 0:
                continue

            outro_id = m["remetente__id"] if m["remetente__id"] != user.id else m["destinatario__id"]
            outro_username = m["remetente__username"] if m["remetente__id"] != user.id else m["destinatario__username"]
            foto_url = perfis_map.get(outro_id, "https://via.placeholder.com/60")

            if outro_id not in conversas or m["ultima_data"] > conversas[outro_id]["ultima_data"]:
                conversas[outro_id] = {
                    "outro_id": outro_id,
                    "outro_username": outro_username,
                    "total": m["total"],
                    "nao_lidas": m["nao_lidas"],
                    "ultima_data": m["ultima_data"].isoformat() if m["ultima_data"] else None,
                    "foto_perfil_url": foto_url,
                }

        return list(conversas.values())
