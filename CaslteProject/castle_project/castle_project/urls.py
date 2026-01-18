from django.contrib import admin
from django.urls import path, re_path # <--- Додали re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve # <--- Додали serve
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('3d/', views.castle_3d_view, name='castle_3d'),
]

# Це змушує Django віддавати медіа-файли навіть коли DEBUG=False
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]

# Для статики залишаємо як було (хоча WhiteNoise це і так робить)
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)