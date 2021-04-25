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
        return request.user.has_perm('store.change_order')


class OrderView(viewsets.mixins.RetrieveModelMixin,
                viewsets.mixins.UpdateModelMixin,
                viewsets.mixins.ListModelMixin,
                viewsets.GenericViewSet):

    permission_classes = (OrderAccessPolicy,)
    queryset = Order.objects
    serializer_class = OrderSerializer
    filterset_fields = ['user', 'email', 'status']
    ordering = ['id']
