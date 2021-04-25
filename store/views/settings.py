from rest_access_policy import AccessPolicy
from rest_framework import viewsets

from store.models import Settings
from store.serializers import SettingsSerializer


class SettingsAccessPolicy(AccessPolicy):
    statements = [
        {
            "action": ["list", "retrieve"],
            "principal": ["*"],
            "effect": "allow",
            "condition": "can_view_settings",
        },
        {
            "action": ["create", "update", "partial_update", "destroy"],
            "principal": ["*"],
            "effect": "allow",
            "condition": "can_moderate_settings",
        }
    ]

    @staticmethod
    def can_view_settings(request, view, action) -> bool:
        return request.user.has_perm('store.view_settings')

    @staticmethod
    def can_moderate_settings(request, view, action) -> bool:
        return (request.user.has_perm('store.add_settings')
                or request.user.has_perm('store.change_settings')
                or request.user.has_perm('store.delete_settings'))


class SettingsView(viewsets.ModelViewSet):
    permission_classes = (SettingsAccessPolicy, )
    queryset = Settings.objects
    serializer_class = SettingsSerializer
    ordering = ['name']
