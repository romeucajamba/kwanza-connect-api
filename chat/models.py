from django.db import models
import uuid
from django.db import models
from django.utils import timezone


# ─────────────────────────────────────────────
#  Sala de conversa
# ─────────────────────────────────────────────

class Room(models.Model):
    """
    Uma sala é criada quando um utilizador contacta outro
    a partir de uma oferta, ou directamente pelo perfil.
    Suporta salas de dois participantes (direct) e
    salas de grupo (group) para futuras extensões.
    """

    ROOM_TYPE = [
        ('direct', 'Conversa directa'),
        ('offer',  'Ligada a uma oferta'),
    ]

    STATUS = [
        ('active',   'Activa'),
        ('closed',   'Fechada'),
        ('archived', 'Arquivada'),
        ('blocked',  'Bloqueada'),
    ]

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    offer      = models.ForeignKey(
        'offers.Offer',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='chat_rooms'
    )
    room_type  = models.CharField(max_length=10, choices=ROOM_TYPE, default='direct')
    status     = models.CharField(max_length=10, choices=STATUS, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    closed_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Sala'
        verbose_name_plural = 'Salas'
        ordering = ['-created_at']

    def __str__(self):
        members = self.members.select_related('user').all()
        names   = ', '.join(m.user.full_name for m in members[:3])
        return f'Sala [{self.get_room_type_display()}] — {names}'

    def close(self):
        self.status    = 'closed'
        self.closed_at = timezone.now()
        self.save(update_fields=['status', 'closed_at'])

    @property
    def last_message(self):
        return self.messages.filter(is_deleted=False).order_by('-created_at').first()

    def unread_count_for(self, user):
        last_read = self.members.filter(user=user).values_list('last_read_at', flat=True).first()
        qs = self.messages.filter(is_deleted=False).exclude(sender=user)
        if last_read:
            qs = qs.filter(created_at__gt=last_read)
        return qs.count()


# ─────────────────────────────────────────────
#  Membros da sala
# ─────────────────────────────────────────────

class RoomMember(models.Model):
    """
    Regista quem está na sala e a data da última leitura,
    usada para calcular mensagens não lidas.
    """

    id           = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room         = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='members')
    user         = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='chat_memberships'
    )
    is_admin     = models.BooleanField(default=False)
    joined_at    = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Membro da sala'
        unique_together = [['room', 'user']]
        ordering = ['joined_at']

    def __str__(self):
        return f'{self.user.full_name} em {self.room_id}'

    def mark_as_read(self):
        self.last_read_at = timezone.now()
        self.save(update_fields=['last_read_at'])


# ─────────────────────────────────────────────
#  Mensagens
# ─────────────────────────────────────────────

def message_file_upload_path(instance, filename):
    return f'chat/{instance.room_id}/{uuid.uuid4()}_{filename}'


class Message(models.Model):
    """
    Cada mensagem pertence a uma sala. Suporta texto,
    ficheiros/imagens, e respostas encadeadas (reply_to).
    Mensagens apagadas guardam o registo mas ocultam o conteúdo.
    """

    MSG_TYPE = [
        ('text',   'Texto'),
        ('image',  'Imagem'),
        ('file',   'Ficheiro'),
        ('system', 'Evento do sistema'),   # ex: "João entrou na sala"
    ]

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room       = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    sender     = models.ForeignKey(
        'users.User', 
        null=True, blank=True,
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )

    reply_to   = models.ForeignKey(
        'self', null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='replies'
    )

    msg_type   = models.CharField(max_length=10, choices=MSG_TYPE, default='text')
    content    = models.TextField(blank=True)
    file       = models.URLField(max_length=500, null=True, blank=True)
    file_name  = models.CharField(max_length=255, blank=True)   # nome original do ficheiro
    file_size  = models.PositiveIntegerField(null=True, blank=True)  # bytes

    is_deleted = models.BooleanField(default=False)
    is_edited  = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    edited_at  = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = 'Mensagem'
        verbose_name_plural = 'Mensagens'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['room', 'created_at']),
            models.Index(fields=['sender', 'created_at']),
        ]

    def __str__(self):
        preview = self.content[:40] if self.content else f'[{self.get_msg_type_display()}]'
        return f'{self.sender.full_name}: {preview}'

    def soft_delete(self):
        """Apaga o conteúdo mas mantém o registo para não quebrar a thread."""
        self.is_deleted = True
        self.content    = ''
        self.file       = None
        self.save(update_fields=['is_deleted', 'content', 'file'])

    def edit(self, new_content: str):
        self.content   = new_content
        self.is_edited = True
        self.edited_at = timezone.now()
        self.save(update_fields=['content', 'is_edited', 'edited_at'])


# ─────────────────────────────────────────────
#  Leituras de mensagens (visto/não visto)
# ─────────────────────────────────────────────

class MessageRead(models.Model):
    """
    Registo granular de leitura por mensagem e por utilizador.
    Permite mostrar os ticks de 'visto' como no WhatsApp.
    """

    id      = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reads')
    user    = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='message_reads'
    )
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Leitura de mensagem'
        unique_together = [['message', 'user']]
        indexes = [
            models.Index(fields=['message', 'user']),
        ]

    def __str__(self):
        return f'{self.user.full_name} leu {self.message_id} às {self.read_at}'


# ─────────────────────────────────────────────
#  Reacções a mensagens
# ─────────────────────────────────────────────

class MessageReaction(models.Model):
    """
    Reacções tipo emoji a mensagens individuais.
    Cada utilizador só pode ter uma reacção por mensagem.
    """

    EMOJI_CHOICES = [
        ('👍', 'Gosto'),
        ('👎', 'Não gosto'),
        ('😂', 'Engraçado'),
        ('😮', 'Surpresa'),
        ('❤️', 'Coração'),
        ('🤝', 'Acordo'),   # útil para negociação
    ]

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message    = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='reactions')
    user       = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name='message_reactions'
    )
    emoji      = models.CharField(max_length=10, choices=EMOJI_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Reacção'
        unique_together = [['message', 'user']]

    def __str__(self):
        return f'{self.user.full_name} reagiu {self.emoji} a {self.message_id}'


# ─────────────────────────────────────────────
#  Eventos da sala (auditoria)
# ─────────────────────────────────────────────

class RoomEvent(models.Model):
    """
    Log imutável de eventos importantes na sala:
    criação, entrada/saída de membros, bloqueio, acordo, etc.
    Serve também para gerar mensagens de sistema no chat.
    """

    EVENT_TYPE = [
        ('room_created',   'Sala criada'),
        ('member_joined',  'Membro entrou'),
        ('member_left',    'Membro saiu'),
        ('room_closed',    'Sala fechada'),
        ('room_blocked',   'Sala bloqueada'),
        ('deal_proposed',  'Acordo proposto'),
        ('deal_accepted',  'Acordo aceite'),
        ('deal_cancelled', 'Acordo cancelado'),
    ]

    id         = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    room       = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='events')
    actor      = models.ForeignKey(
        'users.User', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='room_events'
    )
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE)
    payload    = models.JSONField(default=dict, blank=True)  # dados extra do evento
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Evento de sala'
        verbose_name_plural = 'Eventos de sala'
        ordering = ['created_at']

    def __str__(self):
        return f'[{self.get_event_type_display()}] sala {self.room_id}'