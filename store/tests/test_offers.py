from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from parameterized import parameterized

from store.models import Good
from store.models import Offer
from store.tests.utils import PermissionTest


class OffersTest(PermissionTest):

    def setUp(self):
        super().setUp()

        self.user, created = get_user_model().objects.update_or_create(
            username='test',
            defaults={'is_superuser': False, 'is_staff': False, 'is_active': True})
        self.client.force_login(self.user)

        self.good, created = Good.objects.get_or_create(name='good')
        self.offer, created = Offer.objects.get_or_create(good=self.good, price=1)

    @parameterized.expand([
        ([], 403, None),
        (["store.view_offer"], 200, 1),
    ])
    def test_list(self, perms, status_code, results_count):
        with self._set_perms(self.user, perms):

            url = reverse('store:offers-list')
            response = self.client.get(url)

            self.assertEqual(status_code, response.status_code, response.content)
            if status_code >= 400:
                return

            results = response.json()['results']
            self.assertEqual(results_count, len(results))

    @parameterized.expand([
        ([], 403),
        (["store.view_offer"], 200),
    ])
    def test_retrieve(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:offers-detail', kwargs={"pk": self.offer.id})
            response = self.client.get(url)

            self.assertEqual(status_code, response.status_code, response.content)
            if status_code >= 400:
                return

            results = response.json()
            self.assertDictEqual(results, {
                "id": self.offer.id,
                "good_id": self.good.id,
                "good": {
                    "id": self.good.id,
                    "name": self.good.name,
                },
                "price": '1.000000',
            })

    @parameterized.expand([
        ([], 403),
        (["store.add_offer", "store.change_offer", "store.delete_offer"], 201),
    ])
    def test_create(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:offers-list')
            data = {'good_id': self.good.id, 'price': 2}
            response = self.client.post(url, data=data, format='json')
            self.assertEqual(status_code, response.status_code, response.content)

            if status_code >= 400:
                return

        with self._set_perms(self.user, ['store.view_offer']):

            created_offer_id = response.json()['id']
            url = reverse('store:offers-detail', kwargs={"pk": created_offer_id})
            response = self.client.get(url)

            self.assertEqual(200, response.status_code, response.content)

            results = response.json()
            self.assertDictEqual(results, {
                'id': created_offer_id,
                "good_id": self.good.id,
                "good": {
                    "id": self.good.id,
                    "name": self.good.name
                },
                "price": '2.000000',
            })

    @parameterized.expand([
        ([], 403),
        (["store.add_offer", "store.change_offer", "store.delete_offer"], 200),
    ])
    def test_update(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:offers-detail', kwargs={"pk": self.offer.id})
            data = {
                "good_id": 1,
                "price": 2,

            }
            response = self.client.put(url, data=data, format='json')
            self.assertEqual(status_code, response.status_code, response.content)

            if status_code >= 400:
                return

        with self._set_perms(self.user, ['store.view_offer']):

            url = reverse('store:offers-detail', kwargs={"pk": self.offer.id})
            response = self.client.get(url)

            self.assertEqual(200, response.status_code, response.content)

            results = response.json()
            self.assertDictEqual(results, {
                'id': self.offer.id,
                "good_id": self.good.id,
                "good": {
                    "id": self.good.id,
                    "name": self.good.name
                },
                "price": '2.000000',
            })

    @parameterized.expand([
        ([], 403),
        (["store.add_offer", "store.change_offer", "store.delete_offer"], 200),
    ])
    def test_partial_update(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:offers-detail', kwargs={"pk": self.offer.id})
            data = {
                "good_id": 1,
            }
            response = self.client.patch(url, data=data, format='json')
            self.assertEqual(status_code, response.status_code, response.content)

            if status_code >= 400:
                return

        with self._set_perms(self.user, ['store.view_offer']):

            url = reverse('store:offers-detail', kwargs={"pk": self.offer.id})
            response = self.client.get(url)

            self.assertEqual(200, response.status_code, response.content)

            results = response.json()
            self.assertDictEqual(results, {
                'id': self.offer.id,
                "good_id": self.good.id,
                "good": {
                    "id": self.good.id,
                    "name": self.good.name
                },
                "price": '1.000000',
            })

    @parameterized.expand([
        ([], 403),
        (["store.add_offer", "store.change_offer", "store.delete_offer"], 204),
    ])
    def test_delete(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:offers-detail', kwargs={"pk": self.offer.id})
            response = self.client.delete(url)
            self.assertEqual(status_code, response.status_code, response.content)

            if status_code >= 400:
                return

        with self._set_perms(self.user, ['store.view_offer']):

            url = reverse('store:offers-detail', kwargs={"pk": self.offer.id})
            response = self.client.get(url)

            self.assertEqual(404, response.status_code, response.content)


class AnonymousOffersTest(PermissionTest):

    def setUp(self):
        super().setUp()

        self.user = AnonymousUser()

        self.good, created = Good.objects.get_or_create(name='good')
        self.offer, created = Offer.objects.get_or_create(good=self.good, price=1)

    @parameterized.expand([
        ([], 401, None),
        (["store.view_offer"], 200, 1),
    ])
    def test_list(self, perms, status_code, results_count):
        with self._set_perms(self.user, perms):

            url = reverse('store:offers-list')
            response = self.client.get(url)

            self.assertEqual(status_code, response.status_code, response.content)
            if status_code >= 400:
                return

            results = response.json()['results']
            self.assertEqual(results_count, len(results))

    @parameterized.expand([
        ([], 401),
        (["store.view_offer"], 200),
    ])
    def test_retrieve(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:offers-detail', kwargs={"pk": self.offer.id})
            response = self.client.get(url)

            self.assertEqual(status_code, response.status_code, response.content)
            if status_code >= 400:
                return

            results = response.json()
            self.assertDictEqual(results, {
                "id": self.offer.id,
                "good_id": mock.ANY,
                "good": {
                    "id": mock.ANY,
                    "name": mock.ANY
                },
                "price": mock.ANY,
            })

    @parameterized.expand([
        ([], 401),
        (["store.add_offer", "store.change_offer", "store.delete_offer"], 201),
    ])
    def test_create(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:offers-list')
            data = {'good_id': self.good.id, 'price': 2}
            response = self.client.post(url, data=data, format='json')
            self.assertEqual(status_code, response.status_code, response.content)

            if status_code >= 400:
                return

        with self._set_perms(self.user, ['store.view_offer']):

            created_offer_id = response.json()['id']
            url = reverse('store:offers-detail', kwargs={"pk": created_offer_id})
            response = self.client.get(url)

            self.assertEqual(200, response.status_code, response.content)

            results = response.json()
            self.assertDictEqual(results, {
                'id': created_offer_id,
                "good_id": self.good.id,
                "good": {
                    "id": self.good.id,
                    "name": self.good.name
                },
                "price": '2.000000',
            })

    @parameterized.expand([
        ([], 401),
        (["store.add_offer", "store.change_offer", "store.delete_offer"], 200),
    ])
    def test_update(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:offers-detail', kwargs={"pk": self.offer.id})
            data = {
                "good_id": 1,
                "price": 2,

            }
            response = self.client.put(url, data=data, format='json')
            self.assertEqual(status_code, response.status_code, response.content)

            if status_code >= 400:
                return

        with self._set_perms(self.user, ['store.view_offer']):

            url = reverse('store:offers-detail', kwargs={"pk": self.offer.id})
            response = self.client.get(url)

            self.assertEqual(200, response.status_code, response.content)

            results = response.json()
            self.assertDictEqual(results, {
                'id': self.offer.id,
                "good_id": self.good.id,
                "good": {
                    "id": self.good.id,
                    "name": self.good.name
                },
                "price": '2.000000',
            })

    @parameterized.expand([
        ([], 401),
        (["store.add_offer", "store.change_offer", "store.delete_offer"], 200),
    ])
    def test_partial_update(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:offers-detail', kwargs={"pk": self.offer.id})
            data = {
                "good_id": 1,
            }
            response = self.client.patch(url, data=data, format='json')
            self.assertEqual(status_code, response.status_code, response.content)

            if status_code >= 400:
                return

        with self._set_perms(self.user, ['store.view_offer']):

            url = reverse('store:offers-detail', kwargs={"pk": self.offer.id})
            response = self.client.get(url)

            self.assertEqual(200, response.status_code, response.content)

            results = response.json()
            self.assertDictEqual(results, {
                'id': self.offer.id,
                "good_id": self.good.id,
                "good": {
                    "id": self.good.id,
                    "name": self.good.name
                },
                "price": '1.000000',
            })

    @parameterized.expand([
        ([], 401),
        (["store.add_offer", "store.change_offer", "store.delete_offer"], 204),
    ])
    def test_delete(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:offers-detail', kwargs={"pk": self.offer.id})
            response = self.client.delete(url)
            self.assertEqual(status_code, response.status_code, response.content)

            if status_code >= 400:
                return

        with self._set_perms(self.user, ['store.view_offer']):

            url = reverse('store:offers-detail', kwargs={"pk": self.offer.id})
            response = self.client.get(url)

            self.assertEqual(404, response.status_code, response.content)
