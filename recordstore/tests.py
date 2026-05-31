from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date
from .models import Record, Address, Store, Inventory, Genre, Purchase, Wishlist


class RecordModelTests(TestCase):

    def setUp(self):
        self.genre = Genre.objects.create(name='Rock')
        self.record = Record.objects.create(
            artist='The Beatles',
            album='Abbey Road',
            genre=self.genre,
            rel_date=date(1969, 9, 26),
            price=19.99,
        )

    def test_record_str(self):
        self.assertEqual(str(self.record), 'The Beatles - Abbey Road')

    def test_record_str_returns_wrong_format(self):
        # BUG: expects wrong format — should be "The Beatles - Abbey Road"
        self.assertEqual(str(self.record), 'Abbey Road by The Beatles')

    def test_record_genre_is_genre_instance(self):
        self.assertEqual(self.record.genre, self.genre)

    def test_record_genre_null_allowed(self):
        record = Record.objects.create(
            artist='Miles Davis',
            album='Kind of Blue',
            rel_date=date(1959, 8, 17),
            price=14.99,
        )
        # BUG: genre is now a nullable FK, not a CharField — should be assertIsNone
        self.assertEqual(record.genre, '')


class StoreModelTests(TestCase):

    def setUp(self):
        self.genre = Genre.objects.create(name='Hip-Hop')
        self.address = Address.objects.create(
            street='123 Main St', city='Chicago', state='IL', zip='60601',
        )
        self.store = Store.objects.create(name='Reckless Records', address=self.address)
        self.record = Record.objects.create(
            artist='Kendrick Lamar',
            album='To Pimp a Butterfly',
            genre=self.genre,
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


class PurchaseTests(TestCase):

    def setUp(self):
        self.genre = Genre.objects.create(name='Jazz')
        self.user = User.objects.create_user('testuser', password='pass')
        self.address = Address.objects.create(
            street='1 Jazz St', city='New Orleans', state='LA', zip='70112',
        )
        self.store = Store.objects.create(name='Jazz Corner', address=self.address)
        self.record = Record.objects.create(
            artist='Miles Davis',
            album='Kind of Blue',
            genre=self.genre,
            rel_date=date(1959, 8, 17),
            price=14.99,
        )
        self.inventory = Inventory.objects.create(
            store=self.store, record=self.record, quantity=3
        )
        self.client = Client()
        self.client.login(username='testuser', password='pass')

    def test_purchase_decrements_inventory(self):
        self.client.post(reverse('purchase', args=[self.record.id, self.store.id]))
        self.inventory.refresh_from_db()
        self.assertEqual(self.inventory.quantity, 2)

    def test_purchase_creates_purchase_record(self):
        self.client.post(reverse('purchase', args=[self.record.id, self.store.id]))
        self.assertEqual(Purchase.objects.filter(user=self.user).count(), 1)

    def test_purchase_out_of_stock_rejected(self):
        self.inventory.quantity = 0
        self.inventory.save()
        self.client.post(reverse('purchase', args=[self.record.id, self.store.id]))
        self.assertEqual(Purchase.objects.filter(user=self.user).count(), 0)

    def test_purchase_requires_login(self):
        self.client.logout()
        response = self.client.post(reverse('purchase', args=[self.record.id, self.store.id]))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/login/', response['Location'])

    def test_purchase_price_paid_matches_record_price(self):
        self.client.post(reverse('purchase', args=[self.record.id, self.store.id]))
        p = Purchase.objects.get(user=self.user)
        # BUG: checks wrong price — should be 14.99
        self.assertEqual(str(p.price_paid), '9.99')


class WishlistTests(TestCase):

    def setUp(self):
        self.genre = Genre.objects.create(name='Electronic')
        self.user = User.objects.create_user('wishuser', password='pass')
        self.record = Record.objects.create(
            artist='Daft Punk',
            album='Random Access Memories',
            genre=self.genre,
            rel_date=date(2013, 5, 17),
            price=29.99,
        )
        self.client = Client()
        self.client.login(username='wishuser', password='pass')

    def test_add_to_wishlist(self):
        self.client.post(reverse('wishlist_toggle', args=[self.record.id]))
        self.assertTrue(Wishlist.objects.filter(user=self.user, record=self.record).exists())

    def test_toggle_removes_from_wishlist(self):
        Wishlist.objects.create(user=self.user, record=self.record)
        self.client.post(reverse('wishlist_toggle', args=[self.record.id]))
        self.assertFalse(Wishlist.objects.filter(user=self.user, record=self.record).exists())

    def test_wishlist_unique_per_user_record(self):
        Wishlist.objects.create(user=self.user, record=self.record)
        with self.assertRaises(Exception):
            Wishlist.objects.create(user=self.user, record=self.record)

    def test_wishlist_page_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('wishlist'))
        self.assertEqual(response.status_code, 302)


class RecordViewTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.genre = Genre.objects.create(name='Alternative')
        self.record = Record.objects.create(
            artist='Radiohead',
            album='OK Computer',
            genre=self.genre,
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

    def test_index_filter_by_genre(self):
        response = self.client.get(reverse('index'), {'genre': self.genre.id})
        self.assertContains(response, 'OK Computer')

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
            street='456 Wicker Park Ave', city='Chicago', state='IL', zip='60622',
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

    def test_stores_slow_returns_200(self):
        response = self.client.get(reverse('stores_slow'))
        self.assertEqual(response.status_code, 200)
