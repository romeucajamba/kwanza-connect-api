"""
Controllers do módulo de transações.
"""
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from app.exceptions import success_response, created_response
from app.pagination import StandardPagination
from ..infra.serializers import TransactionSerializer, TransactionReviewSerializer, TransactionCreateSerializer
from ..services.use_cases import ConfirmDealUseCase, ListUserTransactionsUseCase, RateTransactionUseCase
from ..infra.repositories import DjangoTransactionRepository
from ..infra.services import DjangoOfferService, DjangoChatService, DjangoNotificationService
import uuid
from app.audit_service import audit_log
from rest_framework.exceptions import NotFound


class TransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Transações'])
    def get(self, request):
        repo = DjangoTransactionRepository()
        limit  = int(request.query_params.get('limit', 20))
        
        # We'll use a simplified list for now, as use case currently doesn't support limit
        txs    = ListUserTransactionsUseCase(repo).execute(user_id=request.user.id)
        
        paginator  = StandardPagination()
        page       = paginator.paginate_queryset(txs, request)
        serializer = TransactionSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class TransactionConfirmView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=TransactionCreateSerializer, tags=['Transações'])
    def post(self, request):
        """Dono da oferta confirma que a troca foi concluída."""
        offer_id = request.data.get('offer')
        room_id  = request.data.get('room')
        notes    = request.data.get('notes', '')
        
        if not offer_id or not room_id:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'offer': 'ID da oferta é obrigatório.', 'room': 'ID da sala é obrigatório.'})

        repo = DjangoTransactionRepository()
        offer_service = DjangoOfferService()
        chat_service = DjangoChatService()
        notif_service = DjangoNotificationService()
        
        use_case = ConfirmDealUseCase(repo, offer_service, chat_service, notif_service)
        trans = use_case.execute(
            user_id=request.user.id, 
            offer_id=uuid.UUID(offer_id), 
            room_id=uuid.UUID(room_id), 
            notes=notes
        )
        
        # Auditoria
        audit_log(
            action='TRANSACTION_CONFIRM', 
            resource='transactions', 
            resource_id=trans.id, 
            metadata={'offer_id': offer_id, 'room_id': room_id},
            request=request
        )
        
        return created_response(
            data=TransactionSerializer(trans).data,
            message='Transação confirmada e registada com sucesso.'
        )


class TransactionReviewView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=TransactionReviewSerializer, tags=['Transações'])
    def post(self, request, transaction_id: str):
        """Avaliar um participante de uma transação concluída."""
        rating = request.data.get('rating')
        comment = request.data.get('comment', '')

        if rating is None:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({'rating': 'A nota (rating) é obrigatória.'})

        repo = DjangoTransactionRepository()
        notif_service = DjangoNotificationService()
        
        review = RateTransactionUseCase(repo, notif_service).execute(
            reviewer_id=request.user.id,
            transaction_id=uuid.UUID(transaction_id),
            rating=rating,
            comment=comment
        )
        
        # Auditoria
        audit_log(
            action='TRANSACTION_REVIEW', 
            resource='transactions', 
            resource_id=transaction_id, 
            metadata={'rating': rating},
            request=request
        )
        
        return created_response(
            data=TransactionReviewSerializer(review).data,
            message='Avaliação registada com sucesso.'
        )


class TransactionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Transações'])
    def get(self, request, transaction_id: str):
        repo = DjangoTransactionRepository()
        trans = repo.get_transaction_by_id(uuid.UUID(transaction_id))
        
        if not trans or (trans.seller_id != request.user.id and trans.buyer_id != request.user.id):
            raise NotFound('Transação não encontrada ou não pertence ao utilizador.')
        
        serializer = TransactionSerializer(trans)
        return success_response(data=serializer.data)
