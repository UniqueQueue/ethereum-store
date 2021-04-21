from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

from store.models import Good, Offer, Purchase, Order


def _create_groups():
    groups = {}

    groups['Moderators'], created = Group.objects.get_or_create(name=_('Moderators'))
    groups['Buyers'], created = Group.objects.get_or_create(name=_('Buyers'))

    return groups


def _fill_perms(*, groups):
    good_ct = ContentType.objects.get_for_model(Good)
    view_good = Permission.objects.get(content_type=good_ct, codename='view_good')
    all_good = Permission.objects.filter(content_type=good_ct).all()
    groups['Moderators'].permissions.add(*all_good)
    groups['Buyers'].permissions.add(view_good)

    offer_ct = ContentType.objects.get_for_model(Offer)
    view_offer = Permission.objects.get(content_type=offer_ct, codename='view_offer')
    all_offer = Permission.objects.filter(content_type=offer_ct).all()
    groups['Moderators'].permissions.add(*all_offer)
    groups['Buyers'].permissions.add(view_offer)

    purchase_ct = ContentType.objects.get_for_model(Purchase)
    all_purchase = Permission.objects.filter(content_type=purchase_ct).all()
    groups['Moderators'].permissions.add(*all_purchase)

    order_ct = ContentType.objects.get_for_model(Order)
    view_my_order = Permission.objects.get(content_type=order_ct, codename='view_my_order')
    all_order = Permission.objects.filter(content_type=order_ct).all()
    groups['Moderators'].permissions.add(*all_order)
    groups['Buyers'].permissions.add(view_my_order)

    # permission = Permission.objects.create(
    #     codename='can_publish',
    #     name='Can Publish Posts',
    #     content_type=content_type,
    # )


def populate_models(sender, **kwargs):
    groups = _create_groups()
    _fill_perms(groups=groups)
