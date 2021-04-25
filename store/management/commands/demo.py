from itertools import count, cycle

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from store import initialization
from store.models import Good, Offer, Purchase
from store.models import Order


def _get_groups():
    groups = {g.name: g for g in Group.objects.all()}
    return groups


def _create_users(*, groups):
    users = {}

    admin, created = get_user_model().objects.update_or_create(
        username='admin',
        defaults={'is_superuser': True, 'is_staff': True, 'is_active': True})
    admin.set_password('admin')
    admin.save()
    users['admin'] = admin

    moderator, created = get_user_model().objects.update_or_create(
        username='moderator',
        defaults={'is_superuser': False, 'is_staff': True, 'is_active': True})
    moderator.set_password('moderator')
    moderator.save()
    groups['Moderators'].user_set.add(moderator)
    users['moderator'] = moderator

    buyer, created = get_user_model().objects.update_or_create(
        username='buyer',
        defaults={'is_superuser': False, 'is_staff': True, 'is_active': True})
    buyer.set_password('buyer')
    buyer.save()
    groups['Buyers'].user_set.add(buyer)
    users['buyer'] = buyer

    return users


def _create_goods():
    goods = {}

    for idx in range(1, 16 + 1):
        goods[f'good_{idx}'], created = Good.objects.get_or_create(name=f'good {idx}')

    return goods


def _create_offers(*, goods):
    offers = {}

    for idx in range(1, 10):
        good = goods[f'good_{idx}']
        price = idx
        offers[f'offer_{idx}'], created = Offer.objects.get_or_create(good=good, price=price)

    return offers


def _create_orders(*, users):
    orders = {}

    for idx, status in enumerate(Order.Status.values):
        orders[f'order_{idx}'], created = Order.objects.get_or_create(
            user=users['buyer'], email='buyer@mail.ru', status=status)
        orders[f'order_{idx}'].save()

    for idx, status in enumerate(Order.Status.values, idx):
        orders[f'order_{idx}'], created = Order.objects.get_or_create(
            user=users['moderator'], email='moderator@mail.ru', status=status)
        orders[f'order_{idx}'].save()

    return orders


def _create_purchases(*, goods, orders):
    purchases = {}

    good_it = cycle(goods.values())
    idx_it = count(1)

    for order in orders.values():
        good = next(good_it)
        idx = next(idx_it)
        purchases[f'purchase_{idx}'], created = Purchase.objects.get_or_create(good=good, price=idx, order=order)

    return purchases


class Command(BaseCommand):
    help = 'Generate HelloWorld Dataset'

    OPTIONS = (
    )

    def add_arguments(self, parser):
        for (args, kwargs) in self.OPTIONS:
            parser.add_argument(*args, **kwargs)

    def handle(self, *args, **options):
        initialization.delete_models(self)
        initialization.populate_models(self)

        groups = _get_groups()
        users = _create_users(groups=groups)
        goods = _create_goods()
        offers = _create_offers(goods=goods)
        orders = _create_orders(users=users)
        purchases = _create_purchases(goods=goods, orders=orders)
