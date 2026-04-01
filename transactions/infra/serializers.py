"""
Serializers do módulo de transações.
"""
from rest_framework import serializers
from ..models import Transaction, TransactionReview
from users.infra.serializers import PublicUserSerializer
from offers.infra.serializers import CurrencySerializer


class TransactionSerializer(serializers.ModelSerializer):
    seller = PublicUserSerializer(read_only=True)
    buyer  = PublicUserSerializer(read_only=True)
    give_currency = CurrencySerializer(read_only=True)
    want_currency = CurrencySerializer(read_only=True)

    class Meta:
        model  = Transaction
        fields = [
            'id', 'offer', 'room', 'seller', 'buyer',
            'give_currency', 'give_amount',
            'want_currency', 'want_amount',
            'rate', 'status', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields


class TransactionReviewSerializer(serializers.ModelSerializer):
    reviewer = PublicUserSerializer(read_only=True)
    reviewed = PublicUserSerializer(read_only=True)

    class Meta:
        model  = TransactionReview
        fields = [
            'id', 'transaction', 'reviewer', 'reviewed',
            'rating', 'comment', 'created_at'
        ]
        read_only_fields = ['id', 'reviewer', 'reviewed', 'created_at']

    def validate(self, data):
        # Additional validation could be added here
        return data


class TransactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Transaction
        fields = ['offer', 'room', 'status', 'notes']
