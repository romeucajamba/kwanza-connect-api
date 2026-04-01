"""
Use cases do módulo de transações.
"""
from django.db import transaction
from rest_framework.exceptions import ValidationError, NotFound, PermissionDenied
from ..models import Transaction, TransactionReview
from offers.models import Offer, OfferInterest
from chat.models import Room


class ConfirmDealUseCase:
    """
    Confirma que um acordo foi concluído com sucesso.
    Cria o registo de transação e encerra os objectos relacionados.
    """
    def execute(self, user, offer_id: str, room_id: str, notes: str = '') -> Transaction:
        try:
            offer = Offer.objects.select_related('give_currency', 'want_currency').get(id=offer_id, owner=user)
        except Offer.DoesNotExist:
            raise NotFound('Oferta não encontrada ou não pertence ao utilizador.')

        try:
            room = Room.objects.get(id=room_id, offer=offer)
        except Room.DoesNotExist:
            raise ValidationError('Sala não encontrada ou não está associada a esta oferta.')

        # Encontra o outro participante (comprador) na sala
        member = room.members.exclude(user=user).first()
        if not member:
            raise ValidationError('Não foi possível identificar o comprador nesta sala.')
        
        buyer = member.user

        with transaction.atomic():
            # 1. Cria a transação (histórico imutável)
            trans = Transaction.objects.create(
                offer=offer,
                room=room,
                seller=user,
                buyer=buyer,
                give_currency=offer.give_currency,
                give_amount=offer.give_amount,
                want_currency=offer.want_currency,
                want_amount=offer.want_amount,
                rate=offer.exchange_rate_snapshot, # Snapshot da publicação ou actual? Usamos snapshot original por defeito.
                status='completed',
                notes=notes
            )

            # 2. Encerra a oferta
            offer.status = 'closed'
            offer.save(update_fields=['status', 'updated_at'])

            # 3. Encerra a sala de chat (opcional, mas recomendado)
            room.status = 'closed'
            room.save(update_fields=['status', 'closed_at'])

            # 4. Notificações via NotificationService
            try:
                from notifications.services.notification_service import NotificationService
                from notifications.models import NotificationType
                # Notificar o comprador que a transação foi confirmada
                NotificationService.send(
                    recipient         = buyer,
                    actor             = user,
                    notification_type = NotificationType.SYSTEM,
                    payload           = {
                        'message':  f'A troca com {user.full_name} foi marcada como concluída.',
                        'redirect': f'/transactions/{trans.id}'
                    }
                )
            except Exception:
                pass

        return trans


class ListUserTransactionsUseCase:
    """Lista as transações concluídas de um utilizador."""
    def execute(self, user, limit: int = 50, offset: int = 0):
        from django.db.models import Q
        return Transaction.objects.filter(
            Q(seller=user) | Q(buyer=user)
        ).select_related('seller', 'buyer', 'give_currency', 'want_currency').order_by('-created_at')[offset:offset+limit]


class RateTransactionUseCase:
    """Permite aos participantes avaliarem-se mutuamente após uma transação."""
    def execute(self, reviewer, transaction_id: str, rating: int, comment: str = '') -> TransactionReview:
        try:
            trans = Transaction.objects.get(id=transaction_id)
        except Transaction.DoesNotExist:
            raise NotFound('Transação não encontrada.')

        # Valida se quem avalia é participante
        if reviewer == trans.seller:
            reviewed = trans.buyer
        elif reviewer == trans.buyer:
            reviewed = trans.seller
        else:
            raise PermissionDenied('Apenas os participantes da transação podem avaliá-la.')

        if TransactionReview.objects.filter(transaction=trans, reviewer=reviewer).exists():
            raise ValidationError('Já avaliou esta transação.')

        review = TransactionReview.objects.create(
            transaction=trans,
            reviewer=reviewer,
            reviewed=reviewed,
            rating=rating,
            comment=comment
        )
        
        # Notificar quem recebeu a avaliação
        try:
            from notifications.services.notification_service import NotificationService
            from notifications.models import NotificationType
            NotificationService.send(
                recipient         = reviewed,
                actor             = reviewer,
                notification_type = NotificationType.SYSTEM,
                payload           = {
                    'message':  f'{reviewer.full_name} avaliou a sua troca com {rating} estrelas.',
                    'redirect': f'/profile/reviews'
                }
            )
        except Exception:
            pass

        return review
