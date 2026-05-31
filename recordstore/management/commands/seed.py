import random
from datetime import date
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from recordstore.models import Genre, Record, Address, Store, Inventory

RECORDS = [
    ('The Beatles', 'Abbey Road', 'Rock', date(1969, 9, 26), '18.99'),
    ('The Beatles', "Sgt. Pepper's Lonely Hearts Club Band", 'Rock', date(1967, 6, 1), '16.99'),
    ('Miles Davis', 'Kind of Blue', 'Jazz', date(1959, 8, 17), '14.99'),
    ('Miles Davis', 'Bitches Brew', 'Jazz', date(1970, 3, 30), '19.99'),
    ('John Coltrane', 'A Love Supreme', 'Jazz', date(1965, 1, 17), '14.99'),
    ('Billie Holiday', 'Lady in Satin', 'Jazz', date(1958, 8, 25), '14.99'),
    ('Nina Simone', 'I Put a Spell on You', 'Jazz', date(1965, 1, 1), '15.99'),
    ('Kendrick Lamar', 'To Pimp a Butterfly', 'Hip-Hop', date(2015, 3, 15), '24.99'),
    ('Kendrick Lamar', 'DAMN.', 'Hip-Hop', date(2017, 4, 14), '22.99'),
    ('Outkast', 'Stankonia', 'Hip-Hop', date(2000, 10, 31), '19.99'),
    ('Kanye West', 'My Beautiful Dark Twisted Fantasy', 'Hip-Hop', date(2010, 11, 22), '22.99'),
    ('Radiohead', 'OK Computer', 'Alternative', date(1997, 5, 21), '21.99'),
    ('Radiohead', 'Kid A', 'Alternative', date(2000, 10, 2), '21.99'),
    ('Nirvana', 'Nevermind', 'Alternative', date(1991, 9, 24), '18.99'),
    ('Jeff Buckley', 'Grace', 'Alternative', date(1994, 8, 23), '19.99'),
    ('Daft Punk', 'Random Access Memories', 'Electronic', date(2013, 5, 17), '29.99'),
    ('Aphex Twin', 'Selected Ambient Works 85-92', 'Electronic', date(1992, 11, 9), '22.99'),
    ('LCD Soundsystem', 'Sound of Silver', 'Electronic', date(2007, 3, 12), '22.99'),
    ('Pink Floyd', 'The Dark Side of the Moon', 'Rock', date(1973, 3, 1), '21.99'),
    ('Fleetwood Mac', 'Rumours', 'Rock', date(1977, 2, 4), '19.99'),
    ('Bob Dylan', 'Highway 61 Revisited', 'Rock', date(1965, 8, 30), '16.99'),
    ('David Bowie', 'The Rise and Fall of Ziggy Stardust', 'Rock', date(1972, 6, 16), '18.99'),
    ('Joni Mitchell', 'Blue', 'Rock', date(1971, 6, 22), '17.99'),
    ('Stevie Wonder', 'Songs in the Key of Life', 'R&B', date(1976, 9, 28), '24.99'),
    ("Sly & The Family Stone", "There's a Riot Goin' On", 'R&B', date(1971, 11, 1), '17.99'),
    ('Prince', 'Purple Rain', 'R&B', date(1984, 6, 25), '21.99'),
    ('Beyoncé', 'Lemonade', 'R&B', date(2016, 4, 23), '24.99'),
    ('Frank Ocean', 'Blonde', 'R&B', date(2016, 8, 20), '26.99'),
    ('Michael Jackson', 'Thriller', 'Pop', date(1982, 11, 30), '19.99'),
    ('Taylor Swift', 'Folklore', 'Pop', date(2020, 7, 24), '22.99'),
]

STORES = [
    ('Reckless Records', '26 E Madison St', 'Chicago', 'IL', '60602'),
    ('Dusty Groove', '1120 N Ashland Ave', 'Chicago', 'IL', '60622'),
    ('Amoeba Music', '1855 Haight St', 'San Francisco', 'CA', '94117'),
    ('Waterloo Records', '600A N Lamar Blvd', 'Austin', 'TX', '78703'),
    ('Third Man Records', '623 7th Ave S', 'Nashville', 'TN', '37203'),
]


class Command(BaseCommand):
    help = 'Seed the database with sample record store data'

    def add_arguments(self, parser):
        parser.add_argument('--clear', action='store_true', help='Clear existing data before seeding')

    def handle(self, *args, **options):
        random.seed(42)

        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Inventory.objects.all().delete()
            Store.objects.all().delete()
            Address.objects.all().delete()
            Record.objects.all().delete()
            Genre.objects.all().delete()

        genre_names = {r[2] for r in RECORDS}
        genres = {name: Genre.objects.get_or_create(name=name)[0] for name in genre_names}
        self.stdout.write(f'  {len(genres)} genres')

        records = []
        for artist, album, genre_name, rel_date, price in RECORDS:
            record, _ = Record.objects.get_or_create(
                artist=artist, album=album,
                defaults={'genre': genres[genre_name], 'rel_date': rel_date, 'price': price},
            )
            records.append(record)
        self.stdout.write(f'  {len(records)} records')

        stores = []
        for name, street, city, state, zip_code in STORES:
            address, _ = Address.objects.get_or_create(
                street=street, defaults={'city': city, 'state': state, 'zip': zip_code},
            )
            store, _ = Store.objects.get_or_create(name=name, defaults={'address': address})
            stores.append(store)
        self.stdout.write(f'  {len(stores)} stores')

        count = 0
        for store in stores:
            for record in random.sample(records, k=random.randint(18, 26)):
                choice = random.choices(['out', 'low', 'good'], weights=[10, 20, 70])[0]
                qty = 0 if choice == 'out' else (random.randint(1, 3) if choice == 'low' else random.randint(4, 15))
                _, created = Inventory.objects.get_or_create(
                    store=store, record=record, defaults={'quantity': qty},
                )
                if created:
                    count += 1
        self.stdout.write(f'  {count} inventory entries')

        if not User.objects.filter(username='demo').exists():
            User.objects.create_user('demo', 'demo@example.com', 'demo1234')
            self.stdout.write('  demo user created (username=demo, password=demo1234)')

        self.stdout.write(self.style.SUCCESS('Seed complete.'))
