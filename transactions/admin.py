from django.contrib import admin
from .models import Transaction, TransactionReview


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display  = [
        'seller', 'buyer', 'give_amount', 'give_currency',
        'want_amount', 'want_currency', 'status', 'created_at'
    ]
    list_filter   = ['status', 'give_currency', 'want_currency']
    search_fields = ['seller__email', 'buyer__email', 'notes']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(TransactionReview)
class TransactionReviewAdmin(admin.ModelAdmin):
    list_display  = ['reviewer', 'reviewed', 'rating', 'created_at']
    list_filter   = ['rating']
    search_fields = ['reviewer__email', 'reviewed__email', 'comment']
    readonly_fields = ['created_at']
