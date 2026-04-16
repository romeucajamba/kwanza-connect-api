"""
Serializers do módulo offers.
"""
from rest_framework import serializers
from ..models import Currency, ExchangeRate, Offer, OfferInterest, OfferView
from users.infra.serializers import PublicUserSerializer


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Currency
        fields = ['id', 'code', 'name', 'symbol', 'flag_emoji', 'is_active']


class ExchangeRateSerializer(serializers.ModelSerializer):
    from_currency = CurrencySerializer(read_only=True)
    to_currency   = CurrencySerializer(read_only=True)

    class Meta:
        model  = ExchangeRate
        fields = ['from_currency', 'to_currency', 'rate', 'fetched_at']


class OfferCreateSerializer(serializers.Serializer):
    give_currency_code  = serializers.CharField(max_length=10)
    give_amount         = serializers.DecimalField(max_digits=24, decimal_places=2)
    want_currency_code  = serializers.CharField(max_length=10)
    want_amount         = serializers.DecimalField(max_digits=24, decimal_places=2)
    offer_type          = serializers.ChoiceField(choices=Offer.OFFER_TYPE, default='sell')
    notes               = serializers.CharField(max_length=500, required=False, allow_blank=True)
    city                = serializers.CharField(max_length=100, required=False, allow_blank=True)
    country_code        = serializers.CharField(max_length=5, required=False, allow_blank=True)
    expires_at          = serializers.DateTimeField(required=False, allow_null=True)

    def validate(self, data):
        if data.get('give_currency_code') == data.get('want_currency_code'):
            raise serializers.ValidationError('As moedas de origem e destino não podem ser iguais.')
        if data.get('give_amount', 0) <= 0 or data.get('want_amount', 0) <= 0:
            raise serializers.ValidationError('Os valores têm de ser positivos.')
        return data



class OfferSerializer(serializers.ModelSerializer):
    owner         = PublicUserSerializer(read_only=True)
    give_currency = CurrencySerializer(read_only=True)
    want_currency = CurrencySerializer(read_only=True)
    spread_percentage = serializers.FloatField(read_only=True)
    is_active     = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Offer
        fields = [
            'id', 'owner',
            'give_currency', 'give_amount',
            'want_currency', 'want_amount',
            'exchange_rate_snapshot', 'implied_rate', 'spread_percentage',
            'offer_type', 'status', 'is_active',
            'notes', 'city', 'country_code',
            'views_count', 'expires_at', 'created_at', 'updated_at',
        ]


class OfferInterestCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = OfferInterest
        fields = ['message']


class OfferInterestSerializer(serializers.ModelSerializer):
    buyer = PublicUserSerializer(read_only=True)

    class Meta:
        model  = OfferInterest
        fields = [
            'id', 'buyer', 'status', 'message',
            'room', 'created_at', 'responded_at',
        ]
