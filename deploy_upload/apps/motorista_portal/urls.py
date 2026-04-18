from django.urls import path
from django.contrib.auth import views as auth_views

from . import views
from .views_abastecimentos import lista_abastecimentos

app_name = 'motorista_portal'

urlpatterns = [
    path('login/', views.login_motorista, name='login'),
    path('logout/', views.logout_motorista, name='logout'),
    path('recuperar-senha/', auth_views.PasswordResetView.as_view(
        template_name='motorista_portal/password_reset.html',
        email_template_name='motorista_portal/password_reset_email.html',
        subject_template_name='motorista_portal/password_reset_subject.txt',
        success_url='/motorista/recuperar-senha/enviado/',
    ), name='password_reset'),
    path('recuperar-senha/enviado/', auth_views.PasswordResetDoneView.as_view(
        template_name='motorista_portal/password_reset_done.html',
    ), name='password_reset_done'),
    path('redefinir-senha/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='motorista_portal/password_reset_confirm.html',
        success_url='/motorista/redefinir-senha/concluido/',
    ), name='password_reset_confirm'),
    path('redefinir-senha/concluido/', auth_views.PasswordResetCompleteView.as_view(
        template_name='motorista_portal/password_reset_complete.html',
    ), name='password_reset_complete'),
    path('', views.painel, name='painel'),
    path('documentos-caminhoes/', views.documentos_caminhoes, name='documentos-caminhoes'),
    path('carga/<int:pk>/', views.carga_detalhe, name='carga-detalhe'),
    path('carga/<int:carga_pk>/checklist/', views.checklist_criar, name='checklist-criar'),
    path('carga/<int:carga_pk>/abastecimento/', views.abastecimento_rapido, name='abastecimento-rapido'),
    path('carga/<int:carga_pk>/abastecimento-embutido/', views.abastecimento_embutido, name='abastecimento-embutido'),
    path('checklist/<int:pk>/', views.checklist_detalhe, name='checklist-detalhe'),
    path('carga/<int:carga_pk>/despesa/', views.despesa_criar, name='despesa-criar'),
    path('despesa/<int:pk>/', views.despesa_detalhe, name='despesa-detalhe'),
    path('api/quadro-avisos/', views.quadro_avisos_api, name='quadro-avisos-api'),
    path('abastecimentos/', lista_abastecimentos, name='abastecimentos-list'),
]
