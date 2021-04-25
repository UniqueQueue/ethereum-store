from contextlib import contextmanager
from functools import reduce
from operator import or_
from unittest import mock

from django.conf import settings
from django.contrib.auth.models import Permission
from django.db.models import Q
from rest_framework.test import APITestCase


class PermissionTest(APITestCase):

    @contextmanager
    def _set_perms(self, user, perms):
        if perms:
            q = reduce(or_, [Q(content_type__app_label=perm.split('.')[0]) & Q(codename=perm.split('.')[1])
                             for perm in perms])
            perm_pairs = Permission.objects.filter(q).values_list('content_type__app_label', 'codename')
            existing_perms = {f'{app_label}.{codename}' for app_label, codename in perm_pairs}

            self.assertSetEqual(set(perms), existing_perms, 'Some permissions do not exist. Typo?')

        patch = [None]

        def handler(_self, current_user, *args, **kwargs):
            if user.id == current_user.id:
                return set(perms)

            backend = patch[0].target()
            original = patch[0].temp_original
            return original(backend, current_user, *args, **kwargs)

        patch[0] = mock.patch(f'{settings.AUTHENTICATION_BACKENDS[0]}.get_all_permissions', handler)

        with patch[0]:
            yield
