from rest_access_policy import AccessPolicy
from rest_framework import viewsets

from .models import Good
from .serializers import GoodSerializer


class GoodsAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": ["*"],
            "effect": "allow",
            "condition": "view_good",
        },
    ]

    def view_good(self, request, view, action) -> bool:
        return request.user.has_perm('store.view_good')


class GoodsView(viewsets.ModelViewSet):
    permission_classes = (GoodsAccessPolicy, )
    queryset = Good.objects.all()
    serializer_class = GoodSerializer
