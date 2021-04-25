from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.urls import reverse
from parameterized import parameterized

from store.models import Good
from store.tests.utils import PermissionTest


class GoodsTest(PermissionTest):

    def setUp(self):
        super().setUp()

        self.user, created = get_user_model().objects.update_or_create(
            username='test',
            defaults={'is_superuser': False, 'is_staff': False, 'is_active': True})
        self.client.force_login(self.user)

        self.good, created = Good.objects.get_or_create(name='good')

    @parameterized.expand([
        ([], 403, None),
        (["store.view_good"], 200, 1),
    ])
    def test_list(self, perms, status_code, results_count):
        with self._set_perms(self.user, perms):

            url = reverse('store:goods-list')
            response = self.client.get(url)

            self.assertEqual(status_code, response.status_code, response.content)
            if status_code >= 400:
                return

            results = response.json()['results']
            self.assertEqual(results_count, len(results))

    @parameterized.expand([
        ([], 403),
        (["store.view_good"], 200),
    ])
    def test_retrieve(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:goods-detail', kwargs={"pk": self.good.id})
            response = self.client.get(url)

            self.assertEqual(status_code, response.status_code, response.content)
            if status_code >= 400:
                return

            results = response.json()
            self.assertDictEqual(results, {
                'id': self.good.id,
                'name': mock.ANY,
            })

    @parameterized.expand([
        ([], 403),
        (["store.add_good", "store.change_good"], 201),
    ])
    def test_create(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:goods-list')
            data = {'name': 'test good'}
            response = self.client.post(url, data=data, format='json')
            self.assertEqual(status_code, response.status_code, response.content)

            if status_code >= 400:
                return

        with self._set_perms(self.user, ['store.view_good']):

            created_good_id = response.json()['id']
            url = reverse('store:goods-detail', kwargs={"pk": created_good_id})
            response = self.client.get(url)

            self.assertEqual(200, response.status_code, response.content)

            results = response.json()
            self.assertDictEqual(results, {
                'id': created_good_id,
                'name': 'test good',
            })

    @parameterized.expand([
        ([], 403),
        (["store.add_good", "store.change_good"], 200),
    ])
    def test_update(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:goods-detail', kwargs={"pk": self.good.id})
            data = {'name': 'test good'}
            response = self.client.put(url, data=data, format='json')
            self.assertEqual(status_code, response.status_code, response.content)

            if status_code >= 400:
                return

        with self._set_perms(self.user, ['store.view_good']):

            url = reverse('store:goods-detail', kwargs={"pk": self.good.id})
            response = self.client.get(url)

            self.assertEqual(200, response.status_code, response.content)

            results = response.json()
            self.assertDictEqual(results, {
                'id': self.good.id,
                'name': 'test good',
            })

    @parameterized.expand([
        ([], 403),
        (["store.add_good", "store.change_good"], 200),
    ])
    def test_partial_update(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:goods-detail', kwargs={"pk": self.good.id})
            data = {'name': 'test good'}
            response = self.client.patch(url, data=data, format='json')
            self.assertEqual(status_code, response.status_code, response.content)

            if status_code >= 400:
                return

        with self._set_perms(self.user, ['store.view_good']):

            url = reverse('store:goods-detail', kwargs={"pk": self.good.id})
            response = self.client.get(url)

            self.assertEqual(200, response.status_code, response.content)

            results = response.json()
            self.assertDictEqual(results, {
                'id': self.good.id,
                'name': 'test good',
            })

    @parameterized.expand([
        ([], 403),
        (["store.delete_good"], 403),
    ])
    def test_destroy(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:goods-detail', kwargs={"pk": self.good.id})
            response = self.client.patch(url)
            self.assertEqual(status_code, response.status_code, response.content)

            if status_code >= 400:
                return

        with self._set_perms(self.user, ['store.view_good']):

            url = reverse('store:goods-detail', kwargs={"pk": self.good.id})
            response = self.client.get(url)

            self.assertEqual(404, response.status_code, response.content)


class AnonymousGoodsTest(PermissionTest):

    def setUp(self):
        super().setUp()
        self.user = AnonymousUser()
        self.good, created = Good.objects.get_or_create(name='good')

    @parameterized.expand([
        ([], 401, None),
        (["store.view_good"], 200, 1),
    ])
    def test_list(self, perms, status_code, results_count):
        with self._set_perms(self.user, perms):

            url = reverse('store:goods-list')
            response = self.client.get(url)

            self.assertEqual(status_code, response.status_code, response.content)
            if status_code >= 400:
                return

            results = response.json()['results']
            self.assertEqual(results_count, len(results))

    @parameterized.expand([
        ([], 401),
        (["store.view_good"], 200),
    ])
    def test_retrieve(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:goods-detail', kwargs={"pk": self.good.id})
            response = self.client.get(url)

            self.assertEqual(status_code, response.status_code, response.content)
            if status_code >= 400:
                return

            results = response.json()
            self.assertDictEqual(results, {
                'id': self.good.id,
                'name': mock.ANY,
            })

    @parameterized.expand([
        ([], 401),
        (["store.add_good", "store.change_good"], 201),
    ])
    def test_create(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:goods-list')
            data = {'name': 'test good'}
            response = self.client.post(url, data=data, format='json')
            self.assertEqual(status_code, response.status_code, response.content)

            if status_code >= 400:
                return

        with self._set_perms(self.user, ['store.view_good']):

            created_good_id = response.json()['id']
            url = reverse('store:goods-detail', kwargs={"pk": created_good_id})
            response = self.client.get(url)

            self.assertEqual(200, response.status_code, response.content)

            results = response.json()
            self.assertDictEqual(results, {
                'id': created_good_id,
                'name': 'test good',
            })

    @parameterized.expand([
        ([], 401),
        (["store.add_good", "store.change_good"], 200),
    ])
    def test_update(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:goods-detail', kwargs={"pk": self.good.id})
            data = {'name': 'test good'}
            response = self.client.put(url, data=data, format='json')
            self.assertEqual(status_code, response.status_code, response.content)

            if status_code >= 400:
                return

        with self._set_perms(self.user, ['store.view_good']):

            url = reverse('store:goods-detail', kwargs={"pk": self.good.id})
            response = self.client.get(url)

            self.assertEqual(200, response.status_code, response.content)

            results = response.json()
            self.assertDictEqual(results, {
                'id': self.good.id,
                'name': 'test good',
            })

    @parameterized.expand([
        ([], 401),
        (["store.add_good", "store.change_good"], 200),
    ])
    def test_partial_update(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:goods-detail', kwargs={"pk": self.good.id})
            data = {'name': 'test good'}
            response = self.client.patch(url, data=data, format='json')
            self.assertEqual(status_code, response.status_code, response.content)

            if status_code >= 400:
                return

        with self._set_perms(self.user, ['store.view_good']):

            url = reverse('store:goods-detail', kwargs={"pk": self.good.id})
            response = self.client.get(url)

            self.assertEqual(200, response.status_code, response.content)

            results = response.json()
            self.assertDictEqual(results, {
                'id': self.good.id,
                'name': 'test good',
            })

    @parameterized.expand([
        ([], 401),
        (["store.delete_good"], 401),
    ])
    def test_destroy(self, perms, status_code):
        with self._set_perms(self.user, perms):

            url = reverse('store:goods-detail', kwargs={"pk": self.good.id})
            response = self.client.delete(url)
            self.assertEqual(status_code, response.status_code, response.content)

            if status_code >= 400:
                return

        with self._set_perms(self.user, ['store.view_good']):

            url = reverse('store:goods-detail', kwargs={"pk": self.good.id})
            response = self.client.get(url)

            self.assertEqual(404, response.status_code, response.content)
