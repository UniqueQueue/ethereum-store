import logging
import random

from django.conf import settings
from django.db import IntegrityError
from rest_access_policy import AccessPolicy
from rest_framework import viewsets

from store.const import ORDER_IDS_SESSION_PARAM_NAME
from store.models import Order
from store.serializers import MyOrderSerializer

log = logging.getLogger(__name__)


class MyOrderAccessPolicy(AccessPolicy):
    statements = [
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
    def can_view_my_order(request, view, action) -> bool:
        return request.user.has_perm('store.view_my_order')

    @staticmethod
    def can_moderate_my_order(request, view, action) -> bool:
        return request.user.has_perm('store.moderate_my_order')

    @classmethod
    def scope_queryset(cls, request, view, action, qs):
        if request.user.is_anonymous:
            qs = qs.filter(user=None)  # anonymous is allowed to see anonymous orders only

            if action == 'list':
                order_ids = request.session.get(ORDER_IDS_SESSION_PARAM_NAME, [])
                qs = qs.filter(id__in=order_ids)

        else:
            qs = qs.filter(user=request.user)

        return qs


class MyOrderView(viewsets.ModelViewSet):
    permission_classes = (MyOrderAccessPolicy,)
    queryset = Order.objects
    serializer_class = MyOrderSerializer
    filterset_fields = ['status']
    ordering = ['id']

    @property
    def access_policy(self):
        return self.permission_classes[0]

    def get_queryset(self):
        return self.access_policy.scope_queryset(
            self.request, self, self.action, super().get_queryset()
        )

    def perform_create(self, serializer):
        if not self.request.user.is_anonymous:
            return super().perform_create(serializer)

        # it is allowed to anyone to access an order created by an anonymous user
        # sequential id generation is vulnerable to pickup attacks
        # if one knows his ID, he can guess which one should be next
        # let's make it harder to guess
        for _ in range(settings.ANONYMOUS_ORDER_ID_GENERATION_ITERATIONS):
            try:
                random.seed()
                serializer.validated_data['id'] = random.randint(*settings.ANONYMOUS_ORDER_ID_GENERATION_RANGE)
                super().perform_create(serializer)
                break
            except IntegrityError:
                pass
        else:
            log.exception('Unable to generate anonymous Order-ID.')
            raise

        self.request.session.setdefault(ORDER_IDS_SESSION_PARAM_NAME, []).append(serializer.instance.id)
        self.request.session.modified = True
