from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Record, Store
from .serializers import RecordSerializer, StoreSerializer


def index(request):
    query = request.GET.get('q', '')
    record_list = Record.objects.order_by('-rel_date')
    if query:
        record_list = record_list.filter(
            Q(artist__icontains=query) | Q(album__icontains=query)
        )
    return render(request, 'recordstore/index.html', {'record_list': record_list, 'query': query})


def record_detail(request, record_id):
    record = get_object_or_404(Record, pk=record_id)
    stores = record.store_set.all()
    return render(request, 'recordstore/record_detail.html', {'record': record, 'stores': stores})


def store_list(request):
    stores = Store.objects.select_related('address').all()
    return render(request, 'recordstore/store_list.html', {'stores': stores})


def store_detail(request, store_id):
    store = get_object_or_404(Store, pk=store_id)
    inventory = store.inventory_set.select_related('record').all()
    return render(request, 'recordstore/store_detail.html', {'store': store, 'inventory': inventory})


class RecordViewSet(viewsets.ModelViewSet):
    queryset = Record.objects.all().order_by('-rel_date')
    serializer_class = RecordSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['genre']
    search_fields = ['artist', 'album']
    ordering_fields = ['rel_date', 'price', 'artist']


class StoreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Store.objects.select_related('address').all()
    serializer_class = StoreSerializer
