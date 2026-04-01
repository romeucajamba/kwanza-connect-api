"""
Repositório concreto do módulo de transações.
"""
from typing import Optional, List
from django.db.models import Avg
from ..domain.contracts import ITransactionRepository, ITransactionReviewRepository
from ..domain.entities import TransactionEntity, TransactionReviewEntity
from ..models import Transaction, TransactionReview


class TransactionRepository(ITransactionRepository):

    def _to_entity(self, trans: Transaction) -> TransactionEntity:
        return TransactionEntity(
            id=str(trans.id),
            offer_id=str(trans.offer_id) if trans.offer_id else None,
            room_id=str(trans.room_id) if trans.room_id else None,
            seller_id=str(trans.seller_id),
            buyer_id=str(trans.buyer_id),
            give_currency_code=trans.give_currency.code,
            give_amount=trans.give_amount,
            want_currency_code=trans.want_currency.code,
            want_amount=trans.want_amount,
            rate=trans.rate,
            status=trans.status,
            notes=trans.notes,
            created_at=trans.created_at,
            updated_at=trans.updated_at
        )

    def get_by_id(self, transaction_id: str) -> Optional[TransactionEntity]:
        try:
            return self._to_entity(Transaction.objects.get(id=transaction_id))
        except Transaction.DoesNotExist:
            return None

    def list_by_user(self, user_id: str, limit: int = 50, offset: int = 0) -> List[TransactionEntity]:
        from django.db.models import Q
        trans_list = Transaction.objects.filter(
            Q(seller_id=user_id) | Q(buyer_id=user_id)
        ).order_by('-created_at')[offset:offset+limit]
        return [self._to_entity(t) for t in trans_list]

    def create(self, **data) -> TransactionEntity:
        trans = Transaction.objects.create(**data)
        return self._to_entity(trans)

    def update_status(self, transaction_id: str, status: str) -> None:
        Transaction.objects.filter(id=transaction_id).update(status=status)


class TransactionReviewRepository(ITransactionReviewRepository):

    def _to_entity(self, review: TransactionReview) -> TransactionReviewEntity:
        return TransactionReviewEntity(
            id=str(review.id),
            transaction_id=str(review.transaction_id),
            reviewer_id=str(review.reviewer_id),
            reviewed_id=str(review.reviewed_id),
            rating=review.rating,
            comment=review.comment,
            created_at=review.created_at
        )

    def get_by_transaction(self, transaction_id: str) -> List[TransactionReviewEntity]:
        reviews = TransactionReview.objects.filter(transaction_id=transaction_id)
        return [self._to_entity(r) for r in reviews]

    def create(self, **data) -> TransactionReviewEntity:
        review = TransactionReview.objects.create(**data)
        return self._to_entity(review)

    def get_average_rating(self, user_id: str) -> float:
        result = TransactionReview.objects.filter(reviewed_id=user_id).aggregate(Avg('rating'))
        return result['rating__avg'] or 0.0
