from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'api/records', views.RecordViewSet)
router.register(r'api/stores', views.StoreViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:record_id>/', views.record_detail, name='record_detail'),
    path('stores/', views.store_list, name='store_list'),
    path('stores/<int:store_id>/', views.store_detail, name='store_detail'),
    path('', include(router.urls)),
]
