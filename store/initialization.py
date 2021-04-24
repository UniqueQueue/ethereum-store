from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from store.models import Good, Offer, Purchase, Order


def _create_groups():
    groups = {}

    groups['Moderators'], created = Group.objects.get_or_create(name='Moderators')
    groups['Buyers'], created = Group.objects.get_or_create(name='Buyers')
    groups['AnonymousBuyers'], created = Group.objects.get_or_create(name='AnonymousBuyers')

    return groups


def _delete_groups():
    Group.objects.filter(name='Moderators').delete()
    Group.objects.filter(name='Buyers').delete()
    Group.objects.filter(name='AnonymousBuyers').delete()


def _create_users(*, groups):
    users = {}

    get_user_model().objects.filter(username=settings.ANONYMOUS_USER_NAME).delete()
    anonymous, created = get_user_model().objects.update_or_create(
        username=settings.ANONYMOUS_USER_NAME,
        password=settings.UNUSABLE_PASSWORD,
        defaults={'is_superuser': False, 'is_staff': False, 'is_active': True})
    anonymous.save()
    groups['AnonymousBuyers'].user_set.add(anonymous)
    users['AnonymousUser'] = anonymous

    return users


def _delete_users():
    get_user_model().objects.filter(username=settings.ANONYMOUS_USER_NAME).delete()


def _fill_perms(*, groups):
    good_ct = ContentType.objects.get_for_model(Good)
    view_good = Permission.objects.get(content_type=good_ct, codename='view_good')
    all_good = Permission.objects.filter(content_type=good_ct).all()
    groups['Moderators'].permissions.add(*all_good)
    groups['Buyers'].permissions.add(view_good)
    groups['AnonymousBuyers'].permissions.add(view_good)

    offer_ct = ContentType.objects.get_for_model(Offer)
    view_offer = Permission.objects.get(content_type=offer_ct, codename='view_offer')
    all_offer = Permission.objects.filter(content_type=offer_ct).all()
    groups['Moderators'].permissions.add(*all_offer)
    groups['Buyers'].permissions.add(view_offer)
    groups['AnonymousBuyers'].permissions.add(view_offer)

    purchase_ct = ContentType.objects.get_for_model(Purchase)
    all_purchase = Permission.objects.filter(content_type=purchase_ct).all()
    view_my_purchase = Permission.objects.get(content_type=purchase_ct, codename='view_my_purchase')
    groups['Moderators'].permissions.add(*all_purchase)
    groups['Buyers'].permissions.add(view_my_purchase)
    groups['AnonymousBuyers'].permissions.add(view_my_purchase)

    order_ct = ContentType.objects.get_for_model(Order)
    view_my_order = Permission.objects.get(content_type=order_ct, codename='view_my_order')
    moderate_my_order = Permission.objects.get(content_type=order_ct, codename='moderate_my_order')
    all_order = Permission.objects.filter(content_type=order_ct).all()
    groups['Moderators'].permissions.add(*all_order)
    groups['Buyers'].permissions.add(view_my_order)
    groups['Buyers'].permissions.add(moderate_my_order)
    groups['AnonymousBuyers'].permissions.add(view_my_order)
    groups['AnonymousBuyers'].permissions.add(moderate_my_order)


def delete_models(*args, **kwargs):
    _delete_users()
    _delete_groups()


def populate_models(*args, **kwargs):
    groups = _create_groups()
    users = _create_users(groups=groups)
    _fill_perms(groups=groups)
