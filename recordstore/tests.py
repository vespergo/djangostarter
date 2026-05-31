from django.test import TestCase, Client
from django.urls import reverse
from datetime import date
from .models import Record, Address, Store, Inventory


class RecordModelTests(TestCase):

    def setUp(self):
        self.record = Record.objects.create(
            artist='The Beatles',
            album='Abbey Road',
            genre='Rock',
            rel_date=date(1969, 9, 26),
            price=19.99,
        )

    def test_record_str(self):
        self.assertEqual(str(self.record), 'The Beatles - Abbey Road')

    def test_record_str_returns_wrong_format(self):
        # BUG: expects wrong format — should be "The Beatles - Abbey Road"
        self.assertEqual(str(self.record), 'Abbey Road by The Beatles')

    def test_record_genre_blank_allowed(self):
        record = Record.objects.create(
            artist='Miles Davis',
            album='Kind of Blue',
            rel_date=date(1959, 8, 17),
            price=14.99,
        )
        self.assertEqual(record.genre, '')


class StoreModelTests(TestCase):

    def setUp(self):
        self.address = Address.objects.create(
            street='123 Main St',
            city='Chicago',
            state='IL',
            zip='60601',
        )
        self.store = Store.objects.create(name='Reckless Records', address=self.address)
        self.record = Record.objects.create(
            artist='Kendrick Lamar',
            album='To Pimp a Butterfly',
            genre='Hip-Hop',
            rel_date=date(2015, 3, 15),
            price=24.99,
        )

    def test_store_str(self):
        self.assertEqual(str(self.store), 'Reckless Records')

    def test_inventory_quantity(self):
        Inventory.objects.create(store=self.store, record=self.record, quantity=5)
        item = self.store.inventory_set.get(record=self.record)
        self.assertEqual(item.quantity, 5)

    def test_inventory_unique_together_raises(self):
        Inventory.objects.create(store=self.store, record=self.record, quantity=3)
        with self.assertRaises(Exception):
            Inventory.objects.create(store=self.store, record=self.record, quantity=1)

    def test_store_record_relationship(self):
        # BUG: uses wrong accessor name — 'albums' does not exist, should be 'records'
        Inventory.objects.create(store=self.store, record=self.record, quantity=2)
        self.assertIn(self.record, self.store.albums.all())


class RecordViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.record = Record.objects.create(
            artist='Radiohead',
            album='OK Computer',
            genre='Alternative',
            rel_date=date(1997, 5, 21),
            price=21.99,
        )

    def test_index_returns_200(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_index_shows_artist(self):
        response = self.client.get(reverse('index'))
        self.assertContains(response, 'Radiohead')

    def test_index_search_by_artist(self):
        response = self.client.get(reverse('index'), {'q': 'Radiohead'})
        self.assertContains(response, 'OK Computer')

    def test_index_search_no_results(self):
        response = self.client.get(reverse('index'), {'q': 'zzznomatch'})
        self.assertContains(response, 'No records found.')

    def test_record_detail_returns_200(self):
        response = self.client.get(reverse('record_detail', args=[self.record.id]))
        self.assertEqual(response.status_code, 200)

    def test_record_detail_404_on_missing(self):
        response = self.client.get(reverse('record_detail', args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_record_detail_shows_price(self):
        # BUG: checks for pound sign instead of dollar sign
        response = self.client.get(reverse('record_detail', args=[self.record.id]))
        self.assertContains(response, '£21.99')


class StoreViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.address = Address.objects.create(
            street='456 Wicker Park Ave',
            city='Chicago',
            state='IL',
            zip='60622',
        )
        self.store = Store.objects.create(name='Dusty Groove', address=self.address)

    def test_store_list_returns_200(self):
        response = self.client.get(reverse('store_list'))
        self.assertEqual(response.status_code, 200)

    def test_store_list_shows_store_name(self):
        response = self.client.get(reverse('store_list'))
        self.assertContains(response, 'Dusty Groove')

    def test_store_detail_returns_200(self):
        response = self.client.get(reverse('store_detail', args=[self.store.id]))
        self.assertEqual(response.status_code, 200)

    def test_store_detail_shows_city(self):
        response = self.client.get(reverse('store_detail', args=[self.store.id]))
        self.assertContains(response, 'Chicago')
