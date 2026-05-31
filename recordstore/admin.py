from django.contrib import admin
from .models import Record, Address, Store, Inventory, Genre, Purchase, Wishlist

admin.site.register([Record, Address, Store, Inventory, Genre, Purchase, Wishlist])
