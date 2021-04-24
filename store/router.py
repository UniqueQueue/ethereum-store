from rest_framework import routers

from .views.good import GoodsView
from .views.my_order import MyOrderView
from .views.offer import OffersView
from .views.order import OrderView
from .views.purchase import PurchaseView

app_name = 'store'
store_api_router = routers.SimpleRouter()
store_api_router.register(
    'goods',
    GoodsView,
    basename='goods'
)
store_api_router.register(
    'offers',
    OffersView,
    basename='offers'
)
store_api_router.register(
    'purchases',
    PurchaseView,
    basename='purchases'
)
store_api_router.register(
    'orders',
    OrderView,
    basename='orders'
)
store_api_router.register(
    'buyer/orders',
    MyOrderView,
    basename='buyer-orders'
)
