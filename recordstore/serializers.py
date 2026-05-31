from rest_framework import serializers
from .models import Record, Address, Store, Inventory, Genre


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'


class RecordSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True)
    genre_id = serializers.PrimaryKeyRelatedField(
        queryset=Genre.objects.all(), source='genre', write_only=True, allow_null=True, required=False
    )

    class Meta:
        model = Record
        fields = ['id', 'artist', 'album', 'genre', 'genre_id', 'rel_date', 'price']


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
