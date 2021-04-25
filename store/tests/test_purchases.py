from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from parameterized import parameterized

from store.const import ORDER_IDS_SESSION_PARAM_NAME
from store.models import Good, Purchase, Order
from store.tests.utils import PermissionTest


class PurchasesTest(PermissionTest):

    def setUp(self):
        super().setUp()

        self.user, created = get_user_model().objects.update_or_create(
            username='test',
            defaults={'is_superuser': False, 'is_staff': False, 'is_active': True})
        self.client.force_login(self.user)

        self.other_user, created = get_user_model().objects.update_or_create(
            username='test2',
            defaults={'is_superuser': False, 'is_staff': False, 'is_active': True})

        self.good, created = Good.objects.get_or_create(name='good')

        self.user_order, created = Order.objects.get_or_create(user=self.user, email='test@mail.ru')
        self.user_purchase, created = Purchase.objects.get_or_create(good=self.good, price=1, order=self.user_order)

        self.other_user_order, created = Order.objects.get_or_create(user=self.other_user, email='test2@mail.ru')
        self.other_user_purchase, created = Purchase.objects.get_or_create(good=self.good, price=1, order=self.other_user_order)

        self.anon_order, created = Order.objects.get_or_create(user=None, email='test3@mail.ru')
        self.anon_purchase, created = Purchase.objects.get_or_create(good=self.good, price=1, order=self.anon_order)

    @parameterized.expand([
        ([], 403, None),
        (["store.view_purchase"], 200, 3),
        (["store.view_my_purchase"], 200, 1),
    ])
    def test_list(self, perms, status_code, results_count):
        with self._set_perms(self.user, perms):

            url = reverse('store:purchases-list')
            response = self.client.get(url)

            self.assertEqual(status_code, response.status_code, response.content)
            if status_code >= 400:
                return

            results = response.json()['results']
            self.assertEqual(results_count, len(results))

    @parameterized.expand([
        ([], 403, lambda self: self.user_purchase.id),
        ([], 403, lambda self: self.other_user_purchase.id),
        ([], 403, lambda self: self.anon_purchase.id),
        (["store.view_purchase"], 200, lambda self: self.user_purchase.id),
        (["store.view_purchase"], 200, lambda self: self.other_user_purchase.id),
        (["store.view_purchase"], 200, lambda self: self.anon_purchase.id),
        (["store.view_my_purchase"], 200, lambda self: self.user_purchase.id),
        (["store.view_my_purchase"], 404, lambda self: self.other_user_purchase.id),
        (["store.view_my_purchase"], 404, lambda self: self.anon_purchase.id),
    ])
    def test_retrieve(self, perms, status_code, get_purchase_id):
        with self._set_perms(self.user, perms):

            url = reverse('store:purchases-detail', kwargs={"pk": get_purchase_id(self)})
            response = self.client.get(url)

            self.assertEqual(status_code, response.status_code, response.content)
            if status_code >= 400:
                return

            results = response.json()
            self.assertDictEqual(results, {
                "id": get_purchase_id(self),
                "good_id": self.good.id,
                "good": {
                    "id": self.good.id,
                    "name": self.good.name
                },
                "price": mock.ANY,
                "order": mock.ANY
            })

    @parameterized.expand([
        ([], 403),
        (["store.add_purchase", "store.change_purchase", "store.delete_purchase"], 403),
    ])
    def test_create(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:purchases-list')
            response = self.client.post(url)
            self.assertEqual(status_code, response.status_code, response.content)

    @parameterized.expand([
        ([], 403),
        (["store.add_purchase", "store.change_purchase", "store.delete_purchase"], 403),
    ])
    def test_update(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:purchases-detail', kwargs={"pk": self.anon_order.id})
            response = self.client.put(url)
            self.assertEqual(status_code, response.status_code, response.content)

    @parameterized.expand([
        ([], 403),
        (["store.add_purchase", "store.change_purchase", "store.delete_purchase"], 403),
    ])
    def test_partial_update(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:purchases-detail', kwargs={"pk": self.anon_order.id})
            response = self.client.patch(url)
            self.assertEqual(status_code, response.status_code, response.content)

    @parameterized.expand([
        ([], 403),
        (["store.add_purchase", "store.change_purchase", "store.delete_purchase"], 403),
    ])
    def test_destroy(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:purchases-detail', kwargs={"pk": self.anon_order.id})
            response = self.client.delete(url)
            self.assertEqual(status_code, response.status_code, response.content)


class AnonymousPurchasesTest(PermissionTest):

    def setUp(self):
        super().setUp()

        self.anon_user = AnonymousUser()

        self.other_user, created = get_user_model().objects.update_or_create(
            username='test2',
            defaults={'is_superuser': False, 'is_staff': False, 'is_active': True})

        good, created = Good.objects.get_or_create(name='good')

        self.other_user_order, created = Order.objects.get_or_create(user=self.other_user, email='test2@mail.ru')
        self.other_user_purchase, created = Purchase.objects.get_or_create(good=good, price=1, order=self.other_user_order)

        self.anon_order, created = Order.objects.get_or_create(user=None, email='test3@mail.ru')
        self.anon_purchase, created = Purchase.objects.get_or_create(good=good, price=1, order=self.anon_order)

    @parameterized.expand([
        ([], 401, 0, lambda self: []),
        ([], 401, None, lambda self: [self.anon_order.id]),
        ([], 401, 0, lambda self: [self.other_user_order.id]),
        (["store.view_purchase"], 200, 2, lambda self: []),
        (["store.view_purchase"], 200, 2, lambda self: [self.anon_order.id]),
        (["store.view_purchase"], 200, 2, lambda self: [self.other_user_order.id]),
        (["store.view_my_purchase"], 200, 0, lambda self: []),
        (["store.view_my_purchase"], 200, 1, lambda self: [self.anon_order.id]),
        (["store.view_my_purchase"], 200, 0, lambda self: [self.other_user_order.id]),
    ])
    def test_list(self, perms, status_code, results_count, get_order_ids):
        with self._set_perms(self.anon_user, perms):
            session = self.client.session
            session[ORDER_IDS_SESSION_PARAM_NAME] = get_order_ids(self)
            session.save()

            url = reverse('store:purchases-list')
            response = self.client.get(url)

            self.assertEqual(status_code, response.status_code, response.content)
            if status_code >= 400:
                return

            results = response.json()['results']
            self.assertEqual(results_count, len(results))

    @parameterized.expand([
        ([], 401, lambda self: [self.anon_order.id]),
        ([], 401, lambda self: [self.other_user_order.id]),
        (["store.view_purchase"], 200, lambda self: [self.anon_order.id]),
        (["store.view_purchase"], 200, lambda self: [self.other_user_order.id]),
        (["store.view_my_purchase"], 200, lambda self: [self.anon_order.id]),
        (["store.view_my_purchase"], 404, lambda self: [self.other_user_order.id]),
    ])
    def test_retrieve(self, perms, status_code, get_order_ids):
        with self._set_perms(self.anon_user, perms):

            session = self.client.session
            session[ORDER_IDS_SESSION_PARAM_NAME] = get_order_ids(self)
            session.save()

            pk = get_order_ids(self)[0]
            url = reverse('store:purchases-detail', kwargs={"pk": pk})
            response = self.client.get(url)

            self.assertEqual(status_code, response.status_code, response.content)
            if status_code >= 400:
                return

            results = response.json()
            self.assertDictEqual(results, {
                "id": pk,
                "good_id": mock.ANY,
                "good": {
                    "id": mock.ANY,
                    "name": mock.ANY
                },
                "price": mock.ANY,
                "order": mock.ANY
            })

    @parameterized.expand([
        ([], 401),
        (["store.add_purchase", "store.change_purchase", "store.delete_purchase"], 401),
    ])
    def test_create(self, perms, status_code):
        with self._set_perms(self.anon_user, perms):

            url = reverse('store:purchases-list')
            response = self.client.post(url)
            self.assertEqual(status_code, response.status_code, response.content)

    @parameterized.expand([
        ([], 401),
        (["store.add_purchase", "store.change_purchase", "store.delete_purchase"], 401),
    ])
    def test_update(self, perms, status_code):
        with self._set_perms(self.anon_user, perms):

            url = reverse('store:purchases-detail', kwargs={"pk": self.anon_order.id})
            response = self.client.put(url)
            self.assertEqual(status_code, response.status_code, response.content)

    @parameterized.expand([
        ([], 401),
        (["store.add_purchase", "store.change_purchase", "store.delete_purchase"], 401),
    ])
    def test_partial_update(self, perms, status_code):
        with self._set_perms(self.anon_user, perms):

            url = reverse('store:purchases-detail', kwargs={"pk": self.anon_order.id})
            response = self.client.patch(url)
            self.assertEqual(status_code, response.status_code, response.content)

    @parameterized.expand([
        ([], 401),
        (["store.add_purchase", "store.change_purchase", "store.delete_purchase"], 401),
    ])
    def test_destroy(self, perms, status_code):
        with self._set_perms(self.anon_user, perms):

            url = reverse('store:purchases-detail', kwargs={"pk": self.anon_order.id})
            response = self.client.delete(url)
            self.assertEqual(status_code, response.status_code, response.content)
