from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'api/records', views.RecordViewSet)
router.register(r'api/stores', views.StoreViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('purchases/', views.purchase_history, name='purchase_history'),
    path('stores/', views.store_list, name='store_list'),
    path('stores/slow/', views.stores_slow, name='stores_slow'),
    path('stores/<int:store_id>/', views.store_detail, name='store_detail'),
    path('<int:record_id>/', views.record_detail, name='record_detail'),
    path('<int:record_id>/purchase/<int:store_id>/', views.purchase, name='purchase'),
    path('<int:record_id>/wishlist/', views.wishlist_toggle, name='wishlist_toggle'),
    path('', include(router.urls)),
]
