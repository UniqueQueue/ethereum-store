from rest_access_policy import AccessPolicy
from rest_framework import viewsets

from store.const import ORDER_IDS_SESSION_PARAM_NAME
from store.models import Purchase
from store.serializers import PurchaseSerializer


class PurchaseAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": ["*"],
            "effect": "allow",
            "condition": "can_view_purchase",
        },
        {
            "action": ["list", "retrieve"],
            "principal": ["*"],
            "effect": "allow",
            "condition": "can_view_my_purchase",
        },
    ]

    @staticmethod
    def can_view_purchase(request, view, action) -> bool:
        return request.user.has_perm('store.view_purchase')

    @staticmethod
    def can_view_my_purchase(request, view, action) -> bool:
        return request.user.has_perm('store.view_my_purchase')

    @classmethod
    def scope_queryset(cls, request, view, action, qs):
        if cls.can_view_purchase(request, view, action):
            pass

        elif cls.can_view_my_purchase(request, view, action):
            if request.user.is_anonymous:
                qs = qs.filter(order__user=None)  # anonymous is allowed to see anonymous purchases only
                order_ids = request.session.get(ORDER_IDS_SESSION_PARAM_NAME, [])

                if order_ids:
                    qs = qs.filter(order_id__in=order_ids)
                else:
                    qs = qs.none()

            else:
                qs = qs.filter(order__user=request.user)

        return qs


class PurchaseView(viewsets.ReadOnlyModelViewSet):
    permission_classes = (PurchaseAccessPolicy,)
    queryset = Purchase.objects
    serializer_class = PurchaseSerializer
    ordering = ['id']

    @property
    def access_policy(self):
        return self.permission_classes[0]

    def get_queryset(self):
        return self.access_policy.scope_queryset(
            self.request, self, self.action, super().get_queryset()
        )
