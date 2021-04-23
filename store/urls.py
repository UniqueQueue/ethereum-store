from django.urls import path

from .views.good import GoodsView
from .views.offer import OffersView
from .views.purchase import PurchaseView
from .views.order import OrderView
from .views.my_order import MyOrderView

urlpatterns_store = [
    path('goods', GoodsView.as_view({
        'get': 'list',
        'post': 'create'})),
    path('goods/<int:id>', GoodsView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'})),
    path('offers', OffersView.as_view({
        'get': 'list',
        'post': 'create'})),
    path('offers/<int:id>', OffersView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'})),
    path('purchases', PurchaseView.as_view({
        'get': 'list'})),
    path('purchases/<int:id>', PurchaseView.as_view({
        'get': 'retrieve'})),
    path('orders', OrderView.as_view({
        'get': 'list',
        'post': 'create'})),
    path('orders/<int:id>', OrderView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'})),
    path('buyer/orders', MyOrderView.as_view({
        'get': 'list',
        'post': 'create'})),
    path('buyer/orders/<int:id>', MyOrderView.as_view({
        'get': 'retrieve',
        'put': 'update',
        'patch': 'partial_update',
        'delete': 'destroy'})),
]
