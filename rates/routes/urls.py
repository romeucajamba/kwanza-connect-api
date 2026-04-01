from django.urls import path
from ..controllers.views import ExchangeRateListView, ConvertCurrencyView, DashboardStatsView

urlpatterns = [
    # Câmbios
    path('',                ExchangeRateListView.as_view(), name='rate-list'),
    path('convert/',        ConvertCurrencyView.as_view(),  name='rate-convert'),

    # Estatísticas
    path('dashboard/',       DashboardStatsView.as_view(),   name='dashboard-stats'),
]
