from contextlib import contextmanager
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from rest_framework.test import APITestCase

from store.models import Purchase


class PermissionTest(APITestCase):

    def _set_perms(self, user, perms):
        purchase_ct = ContentType.objects.get_for_model(Purchase)
        perms_orms = Permission.objects.filter(content_type=purchase_ct, codename__in=perms)
        user.user_permissions.set(perms_orms)
        user.save()

    @staticmethod
    @contextmanager
    def _set_anon_perms(prefix, perms):
        patch = [None]

        def handler(_self, user, *args, **kwargs):
            if user.is_anonymous:
                return {f'{prefix}.{p}' for p in perms}

            original = patch[0].temp_original
            return original(user, *args, **kwargs)

        patch[0] = mock.patch(f'{settings.AUTHENTICATION_BACKENDS[0]}.get_all_permissions', handler)

        with patch[0]:
            yield
