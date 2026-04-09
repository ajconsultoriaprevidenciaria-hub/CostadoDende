from django.urls import path

from .views import CargaCreateView, CargaDeleteView, CargaListView, CargaUpdateView, caminhao_compartimentos_json

app_name = 'fretes'

urlpatterns = [
    path('cargas/', CargaListView.as_view(), name='carga-list'),
    path('cargas/nova/', CargaCreateView.as_view(), name='carga-create'),
    path('cargas/<int:pk>/editar/', CargaUpdateView.as_view(), name='carga-update'),
    path('cargas/<int:pk>/excluir/', CargaDeleteView.as_view(), name='carga-delete'),
    path('caminhao/<int:pk>/compartimentos/', caminhao_compartimentos_json, name='caminhao-compartimentos'),
]
