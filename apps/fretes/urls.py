from django.urls import path

from .views import (
    CargaCreateView, CargaDeleteView, CargaListView, CargaUpdateView,
    buscar_cidades, calcular_distancia, caminhao_compartimentos_json,
    caminhoes_json, carga_selecoes_json, fornecedores_json,
    motoristas_json, produtos_json, reverse_geocode, rota_info,
)

app_name = 'fretes'

urlpatterns = [
    path('cargas/', CargaListView.as_view(), name='carga-list'),
    path('cargas/nova/', CargaCreateView.as_view(), name='carga-create'),
    path('cargas/<int:pk>/editar/', CargaUpdateView.as_view(), name='carga-update'),
    path('cargas/<int:pk>/excluir/', CargaDeleteView.as_view(), name='carga-delete'),
    path('caminhao/<int:pk>/compartimentos/', caminhao_compartimentos_json, name='caminhao-compartimentos'),
    path('api/produtos/', produtos_json, name='produtos-json'),
    path('api/cidades/', buscar_cidades, name='buscar-cidades'),
    path('carga/<int:pk>/selecoes/', carga_selecoes_json, name='carga-selecoes'),
    path('api/distancia/', calcular_distancia, name='calcular-distancia'),
    path('api/reverse-geocode/', reverse_geocode, name='reverse-geocode'),
    path('api/rota/<int:pk>/info/', rota_info, name='rota-info'),
    path('api/caminhoes/', caminhoes_json, name='caminhoes-json'),
    path('api/motoristas/', motoristas_json, name='motoristas-json'),
    path('api/fornecedores/', fornecedores_json, name='fornecedores-json'),
]
