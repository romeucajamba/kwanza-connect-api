"""
Controllers do módulo offers.
"""
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter

from app.exceptions import success_response, created_response, no_content_response
from app.permissions import IsOwner
from app.pagination import StandardPagination
from ..models import Currency, Offer, OfferInterest
from ..infra.serializers import (
    CurrencySerializer, OfferSerializer, OfferCreateSerializer,
    OfferInterestSerializer, OfferInterestCreateSerializer,
)
from ..services.use_cases import (
    CreateOfferUseCase, ListOffersUseCase, GetOfferUseCase,
    PauseOfferUseCase, ResumeOfferUseCase, CloseOfferUseCase,
    ExpressInterestUseCase, AcceptInterestUseCase,
    RejectInterestUseCase, CancelInterestUseCase,
)


# ─────────────────────────────────────────────
#  Moedas
# ─────────────────────────────────────────────

class CurrencyListView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(tags=['Moedas'])
    def get(self, request):
        currencies = Currency.objects.filter(is_active=True)
        serializer = CurrencySerializer(currencies, many=True)
        return success_response(data=serializer.data, message='Lista de moedas disponíveis.')


# ─────────────────────────────────────────────
#  Ofertas
# ─────────────────────────────────────────────

class OfferListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Ofertas'])
    def get(self, request):
        filters = {
            'give_currency': request.query_params.get('give'),
            'want_currency': request.query_params.get('want'),
            'city':          request.query_params.get('city'),
            'min_amount':    request.query_params.get('min_amount'),
            'max_amount':    request.query_params.get('max_amount'),
        }
        qs         = ListOffersUseCase().execute(filters=filters)
        paginator  = StandardPagination()
        page       = paginator.paginate_queryset(qs, request)
        serializer = OfferSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    @extend_schema(request=OfferCreateSerializer, tags=['Ofertas'])
    def post(self, request):
        serializer = OfferCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        offer = CreateOfferUseCase().execute(user=request.user, data=serializer.validated_data)
        return created_response(
            data=OfferSerializer(offer).data,
            message='Oferta publicada com sucesso.'
        )


class MyOfferListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Ofertas'])
    def get(self, request):
        qs         = Offer.objects.filter(owner=request.user).select_related('give_currency', 'want_currency')
        paginator  = StandardPagination()
        page       = paginator.paginate_queryset(qs, request)
        serializer = OfferSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)


class OfferDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Ofertas'])
    def get(self, request, offer_id: str):
        offer      = GetOfferUseCase().execute(offer_id=offer_id, viewer=request.user)
        serializer = OfferSerializer(offer)
        return success_response(data=serializer.data)


class OfferPauseView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Ofertas'])
    def post(self, request, offer_id: str):
        offer = PauseOfferUseCase().execute(user=request.user, offer_id=offer_id)
        return success_response(message='Oferta pausada com sucesso.')


class OfferResumeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Ofertas'])
    def post(self, request, offer_id: str):
        offer = ResumeOfferUseCase().execute(user=request.user, offer_id=offer_id)
        return success_response(message='Oferta retomada com sucesso.')


class OfferCloseView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Ofertas'])
    def post(self, request, offer_id: str):
        CloseOfferUseCase().execute(user=request.user, offer_id=offer_id)
        return success_response(message='Oferta encerrada com sucesso.')


# ─────────────────────────────────────────────
#  Interesses
# ─────────────────────────────────────────────

class ExpressInterestView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(request=OfferInterestCreateSerializer, tags=['Interesses'])
    def post(self, request, offer_id: str):
        serializer = OfferInterestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        interest = ExpressInterestUseCase().execute(
            user=request.user,
            offer_id=offer_id,
            message=serializer.validated_data.get('message', ''),
        )
        return created_response(
            data=OfferInterestSerializer(interest).data,
            message='Interesse registado com sucesso. O vendedor será notificado.'
        )


class OfferInterestListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Interesses'])
    def get(self, request, offer_id: str):
        """Lista os interessados na minha oferta."""
        try:
            offer = Offer.objects.get(id=offer_id, owner=request.user)
        except Offer.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound('Oferta não encontrada ou não pertence ao utilizador.')
        interests  = OfferInterest.objects.filter(offer=offer).select_related('buyer')
        serializer = OfferInterestSerializer(interests, many=True)
        return success_response(data=serializer.data)


class AcceptInterestView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Interesses'])
    def post(self, request, interest_id: str):
        room = AcceptInterestUseCase().execute(user=request.user, interest_id=interest_id)
        return success_response(
            data={'room_id': str(room.id)},
            message='Interesse aceite. A conversa foi iniciada.'
        )


class RejectInterestView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Interesses'])
    def post(self, request, interest_id: str):
        RejectInterestUseCase().execute(user=request.user, interest_id=interest_id)
        return success_response(message='Interesse rejeitado.')


class CancelInterestView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Interesses'])
    def delete(self, request, interest_id: str):
        CancelInterestUseCase().execute(user=request.user, interest_id=interest_id)
        return success_response(message='Interesse cancelado com sucesso.')


class MyInterestListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=['Interesses'])
    def get(self, request):
        """Lista todos os meus interesses em ofertas de outros."""
        interests = OfferInterest.objects.filter(buyer=request.user).select_related(
            'offer__give_currency', 'offer__want_currency', 'offer__owner'
        )
        paginator  = StandardPagination()
        page       = paginator.paginate_queryset(interests, request)
        serializer = OfferInterestSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
