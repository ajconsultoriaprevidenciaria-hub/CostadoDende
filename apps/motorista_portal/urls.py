from django.urls import path

from . import views

app_name = 'motorista_portal'

urlpatterns = [
    path('login/', views.login_motorista, name='login'),
    path('logout/', views.logout_motorista, name='logout'),
    path('', views.painel, name='painel'),
    path('carga/<int:pk>/', views.carga_detalhe, name='carga-detalhe'),
    path('carga/<int:carga_pk>/checklist/', views.checklist_criar, name='checklist-criar'),
    path('checklist/<int:pk>/', views.checklist_detalhe, name='checklist-detalhe'),
    path('carga/<int:carga_pk>/despesa/', views.despesa_criar, name='despesa-criar'),
    path('despesa/<int:pk>/', views.despesa_detalhe, name='despesa-detalhe'),
]
