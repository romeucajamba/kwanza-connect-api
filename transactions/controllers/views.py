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


class TransactionListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Transações'])
    def get(self, request):
        limit  = int(request.query_params.get('limit', 20))
        offset = int(request.query_params.get('offset', 0))
        qs     = ListUserTransactionsUseCase().execute(user=request.user, limit=limit, offset=offset)
        paginator  = StandardPagination()
        page       = paginator.paginate_queryset(qs, request)
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

        trans = ConfirmDealUseCase().execute(user=request.user, offer_id=offer_id, room_id=room_id, notes=notes)
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

        review = RateTransactionUseCase().execute(
            reviewer=request.user,
            transaction_id=transaction_id,
            rating=rating,
            comment=comment
        )
        return created_response(
            data=TransactionReviewSerializer(review).data,
            message='Avaliação registada com sucesso.'
        )


class TransactionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Transações'])
    def get(self, request, transaction_id: str):
        try:
            from ..models import Transaction
            from django.db.models import Q
            trans = Transaction.objects.filter(
                Q(seller=request.user) | Q(buyer=request.user),
                id=transaction_id
            ).select_related('seller', 'buyer', 'give_currency', 'want_currency').get()
        except Transaction.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound('Transação não encontrada ou não pertence ao utilizador.')
        
        serializer = TransactionSerializer(trans)
        return success_response(data=serializer.data)
