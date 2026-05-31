from rest_framework import serializers
from .models import Record, Address, Store, Inventory


class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = '__all__'


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    record = RecordSerializer(read_only=True)

    class Meta:
        model = Inventory
        fields = ['record', 'quantity']


class StoreSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)
    inventory = InventorySerializer(many=True, read_only=True, source='inventory_set')

    class Meta:
        model = Store
        fields = ['id', 'name', 'address', 'inventory']
