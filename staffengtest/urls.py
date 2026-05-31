from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('records/', include('recordstore.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
