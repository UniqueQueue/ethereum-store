from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from store.models import Good


def _create_groups():
    groups = {}

    groups['Admins'], created = Group.objects.get_or_create(name='Admins')
    groups['Buyers'], created = Group.objects.get_or_create(name='Buyers')

    return groups


def _create_perms(*, groups):
    good_ct = ContentType.objects.get_for_model(Good)

    view_good = Permission.objects.get(content_type=good_ct, codename='view_good')
    groups['Admins'].permissions.add(view_good)
    groups['Buyers'].permissions.add(view_good)

    # permission = Permission.objects.create(
    #     codename='can_publish',
    #     name='Can Publish Posts',
    #     content_type=content_type,
    # )


def populate_models(sender, **kwargs):
    groups = _create_groups()
    _create_perms(groups=groups)
