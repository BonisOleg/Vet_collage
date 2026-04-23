import os as _os

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.views.static import serve as _serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('courses/', include('courses.urls')),
    path('webinars/', include('webinars.urls')),
    path('membership/', include('membership.urls')),
    path('blog/', include('blog.urls')),
    path('accounts/', include('accounts.urls')),
    path('payments/', include('payments.urls')),
]

# Обслуговуємо /media/ локально коли Bunny.net не підключений (DEV або Render без ключів).
# Коли BUNNY_PASSWORD присутній — файли йдуть через CDN, цей маршрут не потрібен.
if not _os.environ.get('BUNNY_PASSWORD'):
    urlpatterns += [
        path(
            'media/<path:path>',
            _serve,
            {'document_root': settings.MEDIA_ROOT, 'show_indexes': False},
        ),
    ]
