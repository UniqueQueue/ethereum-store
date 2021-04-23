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

    @classmethod
    def scope_queryset(cls, request, view, action, qs):
        if not cls.can_moderate_offer(request, view, action):
            qs = qs.filter(enabled=True)

        return qs


class OffersView(viewsets.ModelViewSet):
    permission_classes = (OffersAccessPolicy, )
    queryset = Offer.objects
    serializer_class = OfferSerializer
    filterset_fields = ['enabled']
    ordering_fields = ['price']
    ordering = ['id']

    @property
    def access_policy(self):
        return self.permission_classes[0]

    def get_queryset(self):
        return self.access_policy.scope_queryset(
            self.request, self, self.action, super().get_queryset()
        )