import uuid
from django.db import models
from django.utils import timezone


class Transaction(models.Model):
    """
    Registo de um acordo concluído entre dois utilizadores na plataforma.
    É criado quando o dono da oferta confirma que a troca foi bem sucedida.
    """
    STATUS = [
        ('pending',   'Pendente'),
        ('completed', 'Concluída'),
        ('cancelled', 'Cancelada'),
        ('disputed',  'Em disputa'),
    ]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    offer       = models.ForeignKey('offers.Offer', on_delete=models.SET_NULL, null=True, related_name='transactions')
    room        = models.ForeignKey('chat.Room', on_delete=models.SET_NULL, null=True, related_name='transactions')
    
    # Participantes
    seller      = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='sales')
    buyer       = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='purchases')

    # Detalhes da troca (congelados no momento da transação)
    give_currency = models.ForeignKey('offers.Currency', on_delete=models.PROTECT, related_name='transactions_give')
    give_amount   = models.DecimalField(max_digits=24, decimal_places=2)
    want_currency = models.ForeignKey('offers.Currency', on_delete=models.PROTECT, related_name='transactions_want')
    want_amount   = models.DecimalField(max_digits=24, decimal_places=2)
    rate          = models.DecimalField(max_digits=24, decimal_places=8)

    status      = models.CharField(max_length=12, choices=STATUS, default='completed')
    notes       = models.TextField(blank=True)
    
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Transação'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.seller.full_name} ↔ {self.buyer.full_name} | {self.give_amount} {self.give_currency.code} → {self.want_amount} {self.want_currency.code}'


class TransactionReview(models.Model):
    """Avaliação de uma transação por parte do comprador ou vendedor."""
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]

    id          = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='reviews')
    reviewer    = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reviews_given')
    reviewed    = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='reviews_received')
    
    rating      = models.PositiveSmallIntegerField(choices=RATING_CHOICES)
    comment     = models.TextField(max_length=500, blank=True)
    
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Avaliação'
        unique_together = [['transaction', 'reviewer']]

    def __str__(self):
        return f'{self.rating}★ de {self.reviewer.full_name} para {self.reviewed.full_name}'
