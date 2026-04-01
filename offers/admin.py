from django.contrib import admin
from .models import Currency, ExchangeRate, Offer, OfferInterest, OfferView


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display  = ['code', 'name', 'symbol', 'flag_emoji', 'is_active', 'sort_order']
    list_editable = ['is_active', 'sort_order']
    ordering      = ['sort_order']


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display  = ['from_currency', 'to_currency', 'rate', 'fetched_at']
    list_filter   = ['from_currency', 'to_currency']
    readonly_fields = ['fetched_at']


class OfferInterestInline(admin.TabularInline):
    model  = OfferInterest
    extra  = 0
    readonly_fields = ['buyer', 'status', 'message', 'room', 'created_at', 'responded_at']
    can_delete = False


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display  = [
        'owner', 'give_amount', 'give_currency',
        'want_amount', 'want_currency',
        'exchange_rate_snapshot', 'spread_percentage',
        'status', 'views_count', 'created_at'
    ]
    list_filter   = ['status', 'offer_type', 'give_currency', 'want_currency']
    search_fields = ['owner__email', 'owner__full_name']
    readonly_fields = [
        'implied_rate', 'exchange_rate_snapshot',
        'views_count', 'created_at', 'updated_at'
    ]
    inlines = [OfferInterestInline]


@admin.register(OfferInterest)
class OfferInterestAdmin(admin.ModelAdmin):
    list_display  = ['buyer', 'offer', 'status', 'created_at', 'responded_at']
    list_filter   = ['status']
    search_fields = ['buyer__email', 'offer__owner__email']
    readonly_fields = ['created_at', 'responded_at', 'room']