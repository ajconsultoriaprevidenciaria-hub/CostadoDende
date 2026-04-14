from django.urls import path

from . import views
from .views_abastecimentos import lista_abastecimentos

app_name = 'motorista_portal'

urlpatterns = [
    path('login/', views.login_motorista, name='login'),
    path('logout/', views.logout_motorista, name='logout'),
    path('', views.painel, name='painel'),
    path('carga/<int:pk>/', views.carga_detalhe, name='carga-detalhe'),
    path('carga/<int:carga_pk>/checklist/', views.checklist_criar, name='checklist-criar'),
    path('carga/<int:carga_pk>/abastecimento/', views.abastecimento_rapido, name='abastecimento-rapido'),
    path('checklist/<int:pk>/', views.checklist_detalhe, name='checklist-detalhe'),
    path('carga/<int:carga_pk>/despesa/', views.despesa_criar, name='despesa-criar'),
    path('despesa/<int:pk>/', views.despesa_detalhe, name='despesa-detalhe'),
    path('api/quadro-avisos/', views.quadro_avisos_api, name='quadro-avisos-api'),
    path('abastecimentos/', lista_abastecimentos, name='abastecimentos-list'),
]
