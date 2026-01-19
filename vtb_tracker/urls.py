from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),

    # ВАЖНО: подключаем API namespace отдельно
    path('transactions/api/', include(('transactions.api_urls', 'api'), namespace='api')),

    # Обычные web-урлы
    path('transactions/', include('transactions.urls')),

    path('cards/', include('cards.urls')),
    path('analytics/', include('analytics.urls')),
    path('dashboard/', include('dashboard.urls')),

    path('', RedirectView.as_view(url='/transactions/', permanent=False), name='home'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
