from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from apps.motorista_portal.views_abastecimentos import lista_abastecimentos, exportar_abastecimentos_pdf

urlpatterns = [
    path('', include('apps.core.urls')),
    path('operacao/', include('apps.fretes.urls')),
    path('motorista/', include('apps.motorista_portal.urls')),
    path('admin/fretes/abastecimentos/',
         lista_abastecimentos,
         name='admin-abastecimentos-list'),
    path('admin/fretes/abastecimentos/pdf/',
         exportar_abastecimentos_pdf,
         name='admin-abastecimentos-pdf'),
    path('login/',
         auth_views.LoginView.as_view(template_name='auth/login.html'),
         name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(
             next_page='login', http_method_names=['get', 'post', 'options']),
         name='logout'),
    path('recuperar-senha/',
         auth_views.PasswordResetView.as_view(
             template_name='auth/password_reset.html',
             email_template_name='auth/password_reset_email.html',
             subject_template_name='auth/password_reset_subject.txt',
             success_url='/recuperar-senha/enviado/',
         ),
         name='password_reset'),
    path('recuperar-senha/enviado/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='auth/password_reset_done.html', ),
         name='password_reset_done'),
    path('redefinir-senha/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='auth/password_reset_confirm.html',
             success_url='/redefinir-senha/concluido/',
         ),
         name='password_reset_confirm'),
    path('redefinir-senha/concluido/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='auth/password_reset_complete.html', ),
         name='password_reset_complete'),
    path('admin/', admin.site.urls),
    path('dashboard/', include('apps.dashboard.urls')),
]

if settings.DEBUG:
    urlpatterns += [path('__reload__/', include('django_browser_reload.urls'))]

if settings.DEBUG or getattr(settings, 'MEDIA_SERVE_BY_DJANGO', False):
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
