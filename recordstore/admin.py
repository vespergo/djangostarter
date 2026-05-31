from django.contrib import admin
from .models import Record, Address, Store, Inventory

admin.site.register([Record, Address, Store, Inventory])
