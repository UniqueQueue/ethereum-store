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
    ]

    @staticmethod
    def can_view_order(request, view, action) -> bool:
        return (request.user.has_perm('store.view_order')
                or request.user.has_perm('store.view_my_order'))

    @classmethod
    def scope_queryset(cls, request, qs):
        if not request.user.has_perm('store.view_order'):
            if request.user.has_perm('store.view_my_order'):
                qs = qs.filter(user=request.user)
        return qs


class OrderView(viewsets.ReadOnlyModelViewSet):
    permission_classes = (OrderAccessPolicy,)
    queryset = Order.objects.order_by('id')
    serializer_class = OrderSerializer

    @property
    def access_policy(self):
        return self.permission_classes[0]

    def get_queryset(self):
        return self.access_policy.scope_queryset(
            self.request, super().get_queryset()
        )
