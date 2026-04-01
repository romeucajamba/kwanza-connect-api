from django.urls import path
from ..controllers.views import TransactionListView, TransactionConfirmView, TransactionReviewView, TransactionDetailView

urlpatterns = [
    # Transações
    path('',                          TransactionListView.as_view(),    name='transaction-list'),
    path('<str:transaction_id>/',     TransactionDetailView.as_view(),  name='transaction-detail'),
    path('confirm/',                  TransactionConfirmView.as_view(), name='transaction-confirm'),
    path('<str:transaction_id>/review/', TransactionReviewView.as_view(), name='transaction-review'),
]
