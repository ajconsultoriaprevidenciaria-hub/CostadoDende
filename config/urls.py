from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from apps.motorista_portal.views_abastecimentos import lista_abastecimentos

urlpatterns = [
    path('', include('apps.core.urls')),
    path('operacao/', include('apps.fretes.urls')),
    path('motorista/', include('apps.motorista_portal.urls')),
    path('admin/fretes/abastecimentos/', lista_abastecimentos, name='admin-abastecimentos-list'),
    path('login/', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('admin/', admin.site.urls),
    path('dashboard/', include('apps.dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
