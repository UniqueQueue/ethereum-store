from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from parameterized import parameterized

from store.models import Good, Offer, Purchase, Order
from store.tests.utils import PermissionTest
from store.const import ORDER_IDS_SESSION_PARAM_NAME


class MyOrdersTest(PermissionTest):

    def setUp(self):
        super().setUp()

        self.user, created = get_user_model().objects.update_or_create(
            username='test',
            defaults={'is_superuser': False, 'is_staff': False, 'is_active': True})
        self.client.force_login(self.user)

        self.other_user, created = get_user_model().objects.update_or_create(
            username='test2',
            defaults={'is_superuser': False, 'is_staff': False, 'is_active': True})

        self.anon_user = AnonymousUser()

        self.good, created = Good.objects.get_or_create(name='good')
        self.good2, created = Good.objects.get_or_create(name='good2')

        self.offer, created = Offer.objects.get_or_create(good=self.good, price=1)
        self.offer2, created = Offer.objects.get_or_create(good=self.good2, price=1)

        self.user_order, created = Order.objects.get_or_create(user=self.user, email='test@mail.ru')
        self.user_purchase, created = Purchase.objects.get_or_create(good=self.good, price=1, order=self.user_order)

        self.other_user_order, created = Order.objects.get_or_create(user=self.other_user, email='test2@mail.ru')
        self.other_user_purchase, created = Purchase.objects.get_or_create(good=self.good, price=1, order=self.other_user_order)

        self.anon_user_order, created = Order.objects.get_or_create(user=None, email='test3@mail.ru')
        self.anon_user_purchase, created = Purchase.objects.get_or_create(good=self.good, price=1, order=self.anon_user_order)

    @parameterized.expand([
        ([], 403, None, lambda self: []),
        ([], 403, None, lambda self: [self.other_user_order.id]),
        ([], 403, None, lambda self: [self.anon_user_order.id]),
        (["store.view_my_order"], 200, 1, lambda self: []),
        (["store.view_my_order"], 200, 1, lambda self: [self.other_user_order.id]),
        (["store.view_my_order"], 200, 2, lambda self: [self.anon_user_order.id]),
    ])
    def test_list(self, perms, status_code, results_count, get_order_ids):
        with self._set_perms(self.user, perms):

            session = self.client.session
            session[ORDER_IDS_SESSION_PARAM_NAME] = get_order_ids(self)
            session.save()

            url = reverse('store:buyer-orders-list')
            response = self.client.get(url)

            self.assertEqual(status_code, response.status_code, response.content)
            if status_code >= 400:
                return

            results = response.json()['results']
            self.assertEqual(results_count, len(results))

    @parameterized.expand([
        ([], 403, 'user'),
        ([], 403, 'other_user'),
        ([], 403, 'anon_user'),
        (["store.view_my_order"], 200, 'user'),
        (["store.view_my_order"], 404, 'other_user'),
        (["store.view_my_order"], 200, 'anon_user'),
    ])
    def test_retrieve(self, perms, status_code, username):
        user = getattr(self, username)
        order = getattr(self, f'{username}_order')
        purchase = getattr(self, f'{username}_purchase')

        with self._set_perms(self.user, perms):

            url = reverse('store:buyer-orders-detail', kwargs={"pk": order.id})
            response = self.client.get(url)

            self.assertEqual(status_code, response.status_code, response.content)
            if status_code >= 400:
                return

            results = response.json()
            self.assertDictEqual(results, {
                "id": order.id,
                "email": order.email,
                "purchases": [
                    {
                        "id": purchase.id,
                        "good": {
                            "id": self.good.id,
                            "name": self.good.name
                        },
                        "good_id": self.good.id,
                        "price": '1.000000',
                        "order": order.id,
                    }
                ],
                "status": order.status.value,
            })

    @parameterized.expand([
        ([], 403),
        (["store.moderate_my_order"], 201),
    ])
    def test_create(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:buyer-orders-list')
            data = {
                "email": "new@mail.ru",
                "offer_ids": [self.offer.id],
            }
            response = self.client.post(url, data=data, format='json')
            self.assertEqual(status_code, response.status_code, response.content)

            if status_code >= 400:
                return

        with self._set_perms(self.user, ['store.view_my_order']):

            order_id = response.json()['id']
            url = reverse('store:buyer-orders-detail', kwargs={"pk": order_id})
            response = self.client.get(url)

            self.assertEqual(200, response.status_code, response.content)

            results = response.json()
            self.assertDictEqual(results, {
                "id": order_id,
                "email": "new@mail.ru",
                "purchases": [
                    {
                        "id": mock.ANY,
                        "good": {
                            "id": self.offer.good.id,
                            "name": self.offer.good.name
                        },
                        "good_id": self.good.id,
                        "price": '1.000000',
                        "order": order_id,
                    }
                ],
                "status": Order.Status.DRAFT.value,
            })

    @parameterized.expand([
        ([], 403, 'user'),
        ([], 403, 'other_user'),
        ([], 403, 'anon_user'),
        (["store.moderate_my_order"], 200, 'user'),
        (["store.moderate_my_order"], 404, 'other_user'),
        (["store.moderate_my_order"], 200, 'anon_user'),
    ])
    def test_update(self, perms, status_code, username):
        user = getattr(self, username)
        order = getattr(self, f'{username}_order')

        with self._set_perms(self.user, perms):

            url = reverse('store:buyer-orders-detail', kwargs={"pk": order.id})
            data = {
                "email": "new@mail.ru",
                "offer_ids": [self.offer2.id],
            }
            response = self.client.put(url, data=data, format='json')
            self.assertEqual(status_code, response.status_code, response.content)

            if status_code >= 400:
                return

        with self._set_perms(self.user, ['store.view_my_order']):

            url = reverse('store:buyer-orders-detail', kwargs={"pk": order.id})
            response = self.client.get(url)

            self.assertEqual(200, response.status_code, response.content)

            results = response.json()
            self.assertDictEqual(results, {
                "id": order.id,
                "email": "new@mail.ru",
                "purchases": [
                    {
                        "id": mock.ANY,
                        "good": {
                            "id": self.good2.id,
                            "name": self.good2.name
                        },
                        "good_id": self.good2.id,
                        "price": '1.000000',
                        "order": order.id,
                    }
                ],
                "status": Order.Status.DRAFT.value,
            })

    @parameterized.expand([
        ([], 403, 'user'),
        ([], 403, 'other_user'),
        ([], 403, 'anon_user'),
        (["store.moderate_my_order"], 200, 'user'),
        (["store.moderate_my_order"], 404, 'other_user'),
        (["store.moderate_my_order"], 200, 'anon_user'),
    ])
    def test_update(self, perms, status_code, username):
        user = getattr(self, username)
        order = getattr(self, f'{username}_order')

        with self._set_perms(self.user, perms):

            url = reverse('store:buyer-orders-detail', kwargs={"pk": order.id})
            data = {
                "email": "new@mail.ru",
            }
            response = self.client.patch(url, data=data, format='json')
            self.assertEqual(status_code, response.status_code, response.content)

            if status_code >= 400:
                return

        with self._set_perms(self.user, ['store.view_my_order']):

            url = reverse('store:buyer-orders-detail', kwargs={"pk": order.id})
            response = self.client.get(url)

            self.assertEqual(200, response.status_code, response.content)

            results = response.json()
            self.assertDictEqual(results, {
                "id": order.id,
                "email": "new@mail.ru",
                "purchases": [
                    {
                        "id": mock.ANY,
                        "good": {
                            "id": self.good.id,
                            "name": self.good.name
                        },
                        "good_id": self.good.id,
                        "price": '1.000000',
                        "order": order.id,
                    }
                ],
                "status": Order.Status.DRAFT.value,
            })

    # @parameterized.expand([
    #     ([], 403),
    #     (["store.moderate_my_order"], 404),
    # ])
    # def test_destroy(self, perms, status_code):
    #     with self._set_perms(self.user, perms):
    #
    #         url = reverse('store:buyer-orders-detail', kwargs={"pk": self.anon_user_order.id})
    #         response = self.client.delete(url)
    #         self.assertEqual(status_code, response.status_code, response.content)


class AnonymousMyOrdersTest(PermissionTest):

    def setUp(self):
        super().setUp()

        self.other_user, created = get_user_model().objects.update_or_create(
            username='test2',
            defaults={'is_superuser': False, 'is_staff': False, 'is_active': True})

        self.anon_user = AnonymousUser()

        self.good, created = Good.objects.get_or_create(name='good')
        self.good2, created = Good.objects.get_or_create(name='good2')
        self.offer, created = Offer.objects.get_or_create(good=self.good, price=1)
        self.offer2, created = Offer.objects.get_or_create(good=self.good2, price=1)

        self.other_user_order, created = Order.objects.get_or_create(user=self.other_user, email='test2@mail.ru')
        self.other_user_purchase, created = Purchase.objects.get_or_create(good=self.good, price=1, order=self.other_user_order)

        self.anon_user_order, created = Order.objects.get_or_create(user=None, email='test3@mail.ru')
        self.anon_user_purchase, created = Purchase.objects.get_or_create(good=self.good, price=1, order=self.anon_user_order)

    @parameterized.expand([
        ([], 401, None, lambda self: []),
        ([], 401, None, lambda self: [self.other_user_order.id]),
        ([], 401, None, lambda self: [self.anon_user_order.id]),
        (["store.view_my_order"], 200, 0, lambda self: []),
        (["store.view_my_order"], 200, 0, lambda self: [self.other_user_order.id]),
        (["store.view_my_order"], 200, 1, lambda self: [self.anon_user_order.id]),
    ])
    def test_list(self, perms, status_code, results_count, get_order_ids):
        with self._set_perms(self.anon_user, perms):

            session = self.client.session
            session[ORDER_IDS_SESSION_PARAM_NAME] = get_order_ids(self)
            session.save()

            url = reverse('store:buyer-orders-list')
            response = self.client.get(url)

            self.assertEqual(status_code, response.status_code, response.content)
            if status_code >= 400:
                return

            results = response.json()['results']
            self.assertEqual(results_count, len(results))

    @parameterized.expand([
        ([], 401, 'other_user'),
        ([], 401, 'anon_user'),
        (["store.view_my_order"], 404, 'other_user'),
        (["store.view_my_order"], 200, 'anon_user'),
    ])
    def test_retrieve(self, perms, status_code, username):
        user = getattr(self, username)
        order = getattr(self, f'{username}_order')
        purchase = getattr(self, f'{username}_purchase')

        with self._set_perms(self.anon_user, perms):

            url = reverse('store:buyer-orders-detail', kwargs={"pk": order.id})
            response = self.client.get(url)

            self.assertEqual(status_code, response.status_code, response.content)
            if status_code >= 400:
                return

            results = response.json()
            self.assertDictEqual(results, {
                "id": order.id,
                "email": order.email,
                "purchases": [
                    {
                        "id": purchase.id,
                        "good": {
                            "id": self.good.id,
                            "name": self.good.name
                        },
                        "good_id": self.good.id,
                        "price": '1.000000',
                        "order": order.id,
                    }
                ],
                "status": order.status.value,
            })

    @parameterized.expand([
        ([], 401),
        (["store.moderate_my_order"], 201),
    ])
    def test_create(self, perms, status_code):
        with self._set_perms(self.anon_user, perms):

            url = reverse('store:buyer-orders-list')
            data = {
                "email": "new@mail.ru",
                "offer_ids": [self.offer.id],
            }
            response = self.client.post(url, data=data, format='json')
            self.assertEqual(status_code, response.status_code, response.content)

            if status_code >= 400:
                return

        with self._set_perms(self.anon_user, ['store.view_my_order']):

            order_id = response.json()['id']
            url = reverse('store:buyer-orders-detail', kwargs={"pk": order_id})
            response = self.client.get(url)

            self.assertEqual(200, response.status_code, response.content)

            results = response.json()
            self.assertDictEqual(results, {
                "id": order_id,
                "email": "new@mail.ru",
                "purchases": [
                    {
                        "id": mock.ANY,
                        "good": {
                            "id": self.offer.good.id,
                            "name": self.offer.good.name
                        },
                        "good_id": self.good.id,
                        "price": '1.000000',
                        "order": order_id,
                    }
                ],
                "status": Order.Status.DRAFT.value,
            })

            order_ids = self.client.session.get(ORDER_IDS_SESSION_PARAM_NAME, [])
            self.assertIn(order_id, order_ids, 'Order was not bound to session')

    @parameterized.expand([
        ([], 401, 'other_user'),
        ([], 401, 'anon_user'),
        (["store.moderate_my_order"], 404, 'other_user'),
        (["store.moderate_my_order"], 200, 'anon_user'),
    ])
    def test_update(self, perms, status_code, username):
        user = getattr(self, username)
        order = getattr(self, f'{username}_order')

        with self._set_perms(self.anon_user, perms):

            url = reverse('store:buyer-orders-detail', kwargs={"pk": order.id})
            data = {
                "email": "new@mail.ru",
                "offer_ids": [self.offer2.id],
            }
            response = self.client.put(url, data=data, format='json')
            self.assertEqual(status_code, response.status_code, response.content)

            if status_code >= 400:
                return

        with self._set_perms(self.anon_user, ['store.view_my_order']):

            url = reverse('store:buyer-orders-detail', kwargs={"pk": order.id})
            response = self.client.get(url)

            self.assertEqual(200, response.status_code, response.content)

            results = response.json()
            self.assertDictEqual(results, {
                "id": order.id,
                "email": "new@mail.ru",
                "purchases": [
                    {
                        "id": mock.ANY,
                        "good": {
                            "id": self.good2.id,
                            "name": self.good2.name
                        },
                        "good_id": self.good2.id,
                        "price": '1.000000',
                        "order": order.id,
                    }
                ],
                "status": Order.Status.DRAFT.value,
            })

    @parameterized.expand([
        ([], 401, 'other_user'),
        ([], 401, 'anon_user'),
        (["store.moderate_my_order"], 404, 'other_user'),
        (["store.moderate_my_order"], 200, 'anon_user'),
    ])
    def test_partial_update(self, perms, status_code, username):
        user = getattr(self, username)
        order = getattr(self, f'{username}_order')

        with self._set_perms(self.anon_user, perms):

            url = reverse('store:buyer-orders-detail', kwargs={"pk": order.id})
            data = {
                "email": "new@mail.ru",
            }
            response = self.client.patch(url, data=data, format='json')
            self.assertEqual(status_code, response.status_code, response.content)

            if status_code >= 400:
                return

        with self._set_perms(self.anon_user, ['store.view_my_order']):

            url = reverse('store:buyer-orders-detail', kwargs={"pk": order.id})
            response = self.client.get(url)

            self.assertEqual(200, response.status_code, response.content)

            results = response.json()
            self.assertDictEqual(results, {
                "id": order.id,
                "email": "new@mail.ru",
                "purchases": [
                    {
                        "id": mock.ANY,
                        "good": {
                            "id": self.good.id,
                            "name": self.good.name
                        },
                        "good_id": self.good.id,
                        "price": '1.000000',
                        "order": order.id,
                    }
                ],
                "status": Order.Status.DRAFT.value,
            })

    # @parameterized.expand([
    #     ([], 401),
    #     (["store.moderate_my_order"], 401),
    # ])
    # def test_destroy(self, perms, status_code):
    #     with self._set_perms(self.anon_user, perms):
    #
    #         url = reverse('store:buyer-orders-detail', kwargs={"pk": self.anon_user_order.id})
    #         response = self.client.delete(url)
    #         self.assertEqual(status_code, response.status_code, response.content)
