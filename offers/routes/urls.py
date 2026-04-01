from django.urls import path
from ..controllers.views import (
    CurrencyListView,
    OfferListCreateView, MyOfferListView, OfferDetailView,
    OfferPauseView, OfferResumeView, OfferCloseView,
    ExpressInterestView, OfferInterestListView,
    AcceptInterestView, RejectInterestView, CancelInterestView,
    MyInterestListView,
)

urlpatterns = [
    # Moedas
    path('currencies/',                               CurrencyListView.as_view(),         name='currency-list'),

    # Ofertas
    path('',                                          OfferListCreateView.as_view(),       name='offer-list-create'),
    path('mine/',                                     MyOfferListView.as_view(),           name='my-offers'),
    path('<str:offer_id>/',                           OfferDetailView.as_view(),           name='offer-detail'),
    path('<str:offer_id>/pause/',                     OfferPauseView.as_view(),            name='offer-pause'),
    path('<str:offer_id>/resume/',                    OfferResumeView.as_view(),           name='offer-resume'),
    path('<str:offer_id>/close/',                     OfferCloseView.as_view(),            name='offer-close'),

    # Interesses
    path('<str:offer_id>/interests/',                 OfferInterestListView.as_view(),     name='offer-interest-list'),
    path('<str:offer_id>/interest/',                  ExpressInterestView.as_view(),       name='offer-express-interest'),
    path('interests/mine/',                           MyInterestListView.as_view(),        name='my-interests'),
    path('interests/<str:interest_id>/accept/',       AcceptInterestView.as_view(),        name='interest-accept'),
    path('interests/<str:interest_id>/reject/',       RejectInterestView.as_view(),        name='interest-reject'),
    path('interests/<str:interest_id>/cancel/',       CancelInterestView.as_view(),        name='interest-cancel'),
]
