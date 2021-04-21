from rest_access_policy import AccessPolicy
from rest_framework import viewsets

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
    ]

    @staticmethod
    def can_view_purchase(request, view, action) -> bool:
        return request.user.has_perm('store.view_purchase')


class PurchaseView(viewsets.ReadOnlyModelViewSet):
    permission_classes = (PurchaseAccessPolicy,)
    queryset = Purchase.objects.order_by('id')
    serializer_class = PurchaseSerializer
