from rest_access_policy import AccessPolicy
from rest_framework import viewsets

from store.models import Good
from store.serializers import GoodSerializer


class GoodsAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": ["*"],
            "effect": "allow",
            "condition": "can_view_good",
        },
        {
            "action": ["create", "update", "partial_update"],
            "principal": ["*"],
            "effect": "allow",
            "condition": "can_moderate_good",
        }
    ]

    @staticmethod
    def can_view_good(request, view, action) -> bool:
        return request.user.has_perm('store.view_good')

    @staticmethod
    def can_moderate_good(request, view, action) -> bool:
        return (request.user.has_perm('store.add_good')
                or request.user.has_perm('store.change_good'))


class GoodsView(viewsets.mixins.CreateModelMixin,
                viewsets.mixins.RetrieveModelMixin,
                viewsets.mixins.UpdateModelMixin,
                viewsets.mixins.ListModelMixin,
                viewsets.GenericViewSet):
    """goods deletion is prohibited as it leads to deletion of linked orders from history"""

    permission_classes = (GoodsAccessPolicy, )
    queryset = Good.objects
    serializer_class = GoodSerializer
    ordering = ['id']
