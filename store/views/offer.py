from rest_access_policy import AccessPolicy
from rest_framework import viewsets

from store.models import Offer
from store.serializers import OfferSerializer


class OffersAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": ["*"],
            "effect": "allow",
            "condition": "can_view_offer",
        },
        {
            "action": ["create", "update", "partial_update", "delete"],
            "principal": ["*"],
            "effect": "allow",
            "condition": "can_moderate_offer",
        },
    ]

    @staticmethod
    def can_view_offer(request, view, action) -> bool:
        return request.user.has_perm('store.view_offer')

    @staticmethod
    def can_moderate_offer(request, view, action) -> bool:
        return (request.user.has_perm('store.add_offer')
                or request.user.has_perm('store.change_offer')
                or request.user.has_perm('store.delete_offer'))


class OffersView(viewsets.ModelViewSet):
    permission_classes = (OffersAccessPolicy, )
    queryset = Offer.objects.order_by('id')
    serializer_class = OfferSerializer
