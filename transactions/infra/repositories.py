from typing import Optional, List
import uuid
from django.db import transaction
from .models import (
    Transaction as DjangoTransaction,
    TransactionReview as DjangoTransactionReview
)
from ..domain.entities import TransactionEntity, TransactionReviewEntity
from ..domain.interfaces import ITransactionRepository

class DjangoTransactionRepository(ITransactionRepository):
    
    def _transaction_to_entity(self, django_tx: DjangoTransaction) -> TransactionEntity:
        return TransactionEntity(
            id=django_tx.id,
            offer_id=django_tx.offer_id,
            room_id=django_tx.room_id,
            seller_id=django_tx.seller_id,
            buyer_id=django_tx.buyer_id,
            give_currency_id=django_tx.give_currency_id,
            give_amount=django_tx.give_amount,
            want_currency_id=django_tx.want_currency_id,
            want_amount=django_tx.want_amount,
            rate=django_tx.rate,
            status=django_tx.status,
            notes=django_tx.notes,
            created_at=django_tx.created_at,
            updated_at=django_tx.updated_at
        )

    def _review_to_entity(self, django_review: DjangoTransactionReview) -> TransactionReviewEntity:
        return TransactionReviewEntity(
            id=django_review.id,
            transaction_id=django_review.transaction_id,
            reviewer_id=django_review.reviewer_id,
            reviewed_id=django_review.reviewed_id,
            rating=django_review.rating,
            comment=django_review.comment,
            created_at=django_review.created_at
        )

    def save_transaction(self, tx: TransactionEntity) -> TransactionEntity:
        django_tx, created = DjangoTransaction.objects.update_or_create(
            id=tx.id,
            defaults={
                'offer_id': tx.offer_id,
                'room_id':  tx.room_id,
                'seller_id': tx.seller_id,
                'buyer_id': tx.buyer_id,
                'give_currency_id': tx.give_currency_id,
                'give_amount': tx.give_amount,
                'want_currency_id': tx.want_currency_id,
                'want_amount': tx.want_amount,
                'rate': tx.rate,
                'status': tx.status,
                'notes': tx.notes,
            }
        )
        return self._transaction_to_entity(django_tx)

    def get_transaction_by_id(self, tx_id: uuid.UUID) -> Optional[TransactionEntity]:
        try:
            return self._transaction_to_entity(DjangoTransaction.objects.get(id=tx_id))
        except DjangoTransaction.DoesNotExist:
            return None

    def list_user_transactions(self, user_id: uuid.UUID) -> List[TransactionEntity]:
        from django.db.models import Q
        txs = DjangoTransaction.objects.filter(
            Q(seller_id=user_id) | Q(buyer_id=user_id)
        ).order_by('-created_at')
        return [self._transaction_to_entity(tx) for tx in txs]

    def save_review(self, review: TransactionReviewEntity) -> TransactionReviewEntity:
        django_review, created = DjangoTransactionReview.objects.update_or_create(
            id=review.id,
            defaults={
                'transaction_id': review.transaction_id,
                'reviewer_id': review.reviewer_id,
                'reviewed_id': review.reviewed_id,
                'rating': review.rating,
                'comment': review.comment,
            }
        )
        return self._review_to_entity(django_review)

    def get_review_by_transaction_and_user(self, tx_id: uuid.UUID, user_id: uuid.UUID) -> Optional[TransactionReviewEntity]:
        try:
            return self._review_to_entity(DjangoTransactionReview.objects.get(transaction_id=tx_id, reviewer_id=user_id))
        except DjangoTransactionReview.DoesNotExist:
            return None

    def list_user_reviews_received(self, user_id: uuid.UUID) -> List[TransactionReviewEntity]:
        reviews = DjangoTransactionReview.objects.filter(reviewed_id=user_id).order_by('-created_at')
        return [self._review_to_entity(r) for r in reviews]
