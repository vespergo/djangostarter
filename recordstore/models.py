from django.db import models
from django.contrib.auth.models import User


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Genres'
        ordering = ['name']


class Record(models.Model):
    def __str__(self):
        return f'{self.artist} - {self.album}'

    class Meta:
        verbose_name_plural = 'Records'

    artist = models.CharField(max_length=500)
    album = models.CharField(max_length=500)
    genre = models.ForeignKey(Genre, null=True, blank=True, on_delete=models.SET_NULL)
    rel_date = models.DateField()
    price = models.DecimalField(decimal_places=2, max_digits=7)


class Address(models.Model):
    def __str__(self):
        return self.street

    class Meta:
        verbose_name_plural = 'Addresses'

    street = models.CharField(max_length=500)
    city = models.CharField(max_length=500)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=10)


class Store(models.Model):
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Stores'

    name = models.CharField(max_length=500)
    records = models.ManyToManyField(Record, through='Inventory', blank=True)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)


class Inventory(models.Model):
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('store', 'record')
        verbose_name_plural = 'Inventory'

    def __str__(self):
        return f'{self.store.name} - {self.record} (qty: {self.quantity})'


class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    store = models.ForeignKey(Store, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price_paid = models.DecimalField(decimal_places=2, max_digits=7)
    purchased_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = 'Purchases'
        ordering = ['-purchased_at']

    def __str__(self):
        return f'{self.user.username} bought {self.record} from {self.store}'


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    record = models.ForeignKey(Record, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'record')
        verbose_name_plural = 'Wishlists'

    def __str__(self):
        return f'{self.user.username} wants {self.record}'
