from rest_access_policy import AccessPolicy
from rest_framework import viewsets

from store.models import Order
from store.serializers import OrderSerializer


class OrderAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": ["*"],
            "effect": "allow",
            "condition": "can_view_order",
        },
        {
            "action": ["create", "update", "partial_update", "destroy"],
            "principal": ["*"],
            "effect": "allow",
            "condition": "can_moderate_order",
        },
    ]

    @staticmethod
    def can_view_order(request, view, action) -> bool:
        return request.user.has_perm('store.view_order')

    @staticmethod
    def can_moderate_order(request, view, action) -> bool:
        return (request.user.has_perm('store.add_order')
                or request.user.has_perm('store.change_order')
                or request.user.has_perm('store.delete_order'))


class OrderView(viewsets.ModelViewSet):
    permission_classes = (OrderAccessPolicy,)
    queryset = Order.objects
    serializer_class = OrderSerializer
    filterset_fields = ['user', 'email', 'status']
    ordering = ['id']
