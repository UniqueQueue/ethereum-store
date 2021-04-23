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
        {
            "action": ["list", "retrieve"],
            "principal": ["*"],
            "effect": "allow",
            "condition": "can_view_my_order",
        },
        {
            "action": ["create", "update", "partial_update", "destroy"],
            "principal": ["*"],
            "effect": "allow",
            "condition": "can_moderate_my_order",
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

    @staticmethod
    def can_view_my_order(request, view, action) -> bool:
        return request.user.has_perm('store.view_my_order')

    @staticmethod
    def can_moderate_my_order(request, view, action) -> bool:
        return request.user.has_perm('store.moderate_my_order')

    @classmethod
    def scope_queryset(cls, request, view, action, qs):
        if (cls.can_view_order(request, view, action)
                or cls.can_moderate_order(request, view, action)):

            return qs

        if (cls.can_view_my_order(request, view, action)
                or cls.can_moderate_my_order(request, view, action)):

            if not request.user.is_anonymous:
                return qs.filter(user=request.user)

        return qs.none()


class OrderView(viewsets.ModelViewSet):
    permission_classes = (OrderAccessPolicy,)
    queryset = Order.objects.order_by('id')
    serializer_class = OrderSerializer
    filterset_fields = ['email', 'status']

    @property
    def access_policy(self):
        return self.permission_classes[0]

    def get_queryset(self):
        return self.access_policy.scope_queryset(
            self.request, self, self.action, super().get_queryset()
        )
