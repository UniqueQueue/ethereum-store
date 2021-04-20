from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from store.models import Good


def _get_groups():
    groups = {g.name: g for g in Group.objects.all()}
    return groups


def _create_users(*, groups):
    admin, created = get_user_model().objects.update_or_create(
        username='admin',
        defaults={'is_superuser': True, 'is_staff': True, 'is_active': True})
    admin.set_password('admin')
    admin.save()
    groups['Admins'].user_set.add(admin)

    buyer, created = get_user_model().objects.update_or_create(
        username='buyer',
        defaults={'is_superuser': False, 'is_staff': True, 'is_active': True})
    buyer.set_password('buyer')
    buyer.save()
    groups['Buyers'].user_set.add(buyer)


def _create_goods():
    Good.objects.update_or_create(name='good 1', price=1.1)
    Good.objects.update_or_create(name='good 2', price=1.2)


class Command(BaseCommand):
    help = 'Generate HelloWorld Dataset'

    OPTIONS = (
    )

    def add_arguments(self, parser):
        for (args, kwargs) in self.OPTIONS:
            parser.add_argument(*args, **kwargs)

    def handle(self, *args, **options):
        groups = _get_groups()
        _create_users(groups=groups)
        _create_goods()
