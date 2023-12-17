from django.db import models

# Create your models here.
class Record(models.Model):
    def __str__(self):
        return f'{self.artist} - {self.album}'     
    artist = models.CharField(max_length=500)
    album = models.CharField(max_length=500)
    rel_date = models.DateTimeField()
    price = models.DecimalField(decimal_places=2, max_digits=7)

class Address(models.Model):
    def __str__(self):
        return self.street
    street = models.CharField(max_length=500)
    city = models.CharField(max_length=500)
    state = models.CharField(max_length=2)
    zip = models.CharField(max_length=10)

class Store(models.Model):
    name = models.CharField(max_length=500)
    records = models.ForeignKey(Record, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
