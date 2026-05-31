from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Record, Store, Genre, Inventory, Purchase, Wishlist
from .serializers import RecordSerializer, StoreSerializer

VALID_SORTS = {
    'price_asc': 'price',
    'price_desc': '-price',
    'date_asc': 'rel_date',
    'date_desc': '-rel_date',
    'artist': 'artist',
}


def index(request):
    query = request.GET.get('q', '')
    genre_id = request.GET.get('genre', '')
    sort = request.GET.get('sort', 'date_desc')

    record_list = Record.objects.select_related('genre').order_by(VALID_SORTS.get(sort, '-rel_date'))

    if query:
        record_list = record_list.filter(
            Q(artist__icontains=query) | Q(album__icontains=query)
        )
    if genre_id:
        record_list = record_list.filter(genre_id=genre_id)

    paginator = Paginator(record_list, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'recordstore/index.html', {
        'page_obj': page_obj,
        'query': query,
        'genres': Genre.objects.all(),
        'selected_genre': genre_id,
        'sort': sort,
    })


def record_detail(request, record_id):
    record = get_object_or_404(Record.objects.select_related('genre'), pk=record_id)
    inventory = (
        Inventory.objects.filter(record=record)
        .select_related('store__address')
        .order_by('-quantity')
    )
    in_wishlist = (
        request.user.is_authenticated
        and Wishlist.objects.filter(user=request.user, record=record).exists()
    )
    return render(request, 'recordstore/record_detail.html', {
        'record': record,
        'inventory': inventory,
        'in_wishlist': in_wishlist,
    })


@login_required
def purchase(request, record_id, store_id):
    if request.method != 'POST':
        return redirect('record_detail', record_id=record_id)

    with transaction.atomic():
        inventory = get_object_or_404(
            Inventory.objects.select_for_update(),
            record_id=record_id,
            store_id=store_id,
        )
        if inventory.quantity < 1:
            messages.error(request, 'This record is out of stock.')
            return redirect('record_detail', record_id=record_id)

        inventory.quantity -= 1
        inventory.save()

        Purchase.objects.create(
            user=request.user,
            record=inventory.record,
            store=inventory.store,
            price_paid=inventory.record.price,
        )

    messages.success(request, f'You bought {inventory.record}!')
    return redirect('record_detail', record_id=record_id)


@login_required
def wishlist_toggle(request, record_id):
    if request.method != 'POST':
        return redirect('record_detail', record_id=record_id)
    record = get_object_or_404(Record, pk=record_id)
    obj, created = Wishlist.objects.get_or_create(user=request.user, record=record)
    if not created:
        obj.delete()
        messages.info(request, f'Removed {record} from your wishlist.')
    else:
        messages.success(request, f'Added {record} to your wishlist.')
    return redirect('record_detail', record_id=record_id)


@login_required
def wishlist(request):
    items = (
        Wishlist.objects.filter(user=request.user)
        .select_related('record__genre')
        .order_by('-added_at')
    )
    return render(request, 'recordstore/wishlist.html', {'items': items})


@login_required
def purchase_history(request):
    purchases = (
        Purchase.objects.filter(user=request.user)
        .select_related('record__genre', 'store')
    )
    return render(request, 'recordstore/purchase_history.html', {'purchases': purchases})


def store_list(request):
    stores = Store.objects.select_related('address').all()
    return render(request, 'recordstore/store_list.html', {'stores': stores})


def store_detail(request, store_id):
    store = get_object_or_404(Store, pk=store_id)
    inventory = store.inventory_set.select_related('record__genre').all()
    return render(request, 'recordstore/store_detail.html', {'store': store, 'inventory': inventory})


def stores_slow(request):
    # BUG: N+1 — accesses store.address and store.inventory_set per row with no prefetch.
    # Fix: Store.objects.prefetch_related('inventory_set__record').select_related('address')
    stores = Store.objects.all()
    return render(request, 'recordstore/store_list_slow.html', {'stores': stores})


class RecordViewSet(viewsets.ModelViewSet):
    queryset = Record.objects.select_related('genre').order_by('-rel_date')
    serializer_class = RecordSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['genre']
    search_fields = ['artist', 'album']
    ordering_fields = ['rel_date', 'price', 'artist']

    @action(detail=False, methods=['get'])
    def by_price(self, request):
        max_price = request.query_params.get('max_price')
        if max_price:
            # BUG: should be price__lte — returns records MORE expensive than max_price
            queryset = self.get_queryset().filter(price__gte=max_price)
            return Response(self.get_serializer(queryset, many=True).data)
        return Response(self.get_serializer(self.get_queryset(), many=True).data)


class StoreViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Store.objects.select_related('address').all()
    serializer_class = StoreSerializer
