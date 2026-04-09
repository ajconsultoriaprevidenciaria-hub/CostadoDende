from django.urls import path

from .views import (
    CargaCreateView, CargaDeleteView, CargaListView, CargaUpdateView,
    buscar_cidades, calcular_distancia, caminhao_compartimentos_json,
    produtos_json, reverse_geocode,
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
    path('api/distancia/', calcular_distancia, name='calcular-distancia'),
    path('api/reverse-geocode/', reverse_geocode, name='reverse-geocode'),
]
