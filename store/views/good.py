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
        },
        {
            "action": ["delete"],
            "principal": ["*"],
            "effect": "allow",
            "condition": "can_delete_good",
        },
    ]

    @staticmethod
    def can_view_good(request, view, action) -> bool:
        return request.user.has_perm('store.view_good')

    @staticmethod
    def can_moderate_good(request, view, action) -> bool:
        return (request.user.has_perm('store.add_good')
                or request.user.has_perm('store.change_good'))

    @staticmethod
    def can_delete_good(request, view, action) -> bool:
        return request.user.has_perm('store.delete_good')


class GoodsView(viewsets.ModelViewSet):
    permission_classes = (GoodsAccessPolicy, )
    queryset = Good.objects.order_by('id')
    serializer_class = GoodSerializer
