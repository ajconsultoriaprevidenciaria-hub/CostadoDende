import json
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView

from .forms import CargaForm
from .models import Caminhao, Carga, Compartimento


@login_required
def caminhao_compartimentos_json(request, pk):
    try:
        caminhao = Caminhao.objects.get(pk=pk)
    except Caminhao.DoesNotExist:
        return JsonResponse({'compartimentos': []})
    compartimentos = list(
        caminhao.compartimentos.order_by('numero').values('numero', 'capacidade_litros')
    )
    for c in compartimentos:
        c['capacidade_litros'] = float(c['capacidade_litros'])
    return JsonResponse({'compartimentos': compartimentos})


def _salvar_compartimentos(caminhao, dados_raw):
    """Recebe lista de capacidades e atualiza os compartimentos do caminhão."""
    try:
        capacidades = json.loads(dados_raw)
    except (ValueError, TypeError):
        return
    Compartimento.objects.filter(caminhao=caminhao).delete()
    for i, cap in enumerate(capacidades, start=1):
        try:
            Compartimento.objects.create(
                caminhao=caminhao,
                numero=i,
                capacidade_litros=Decimal(str(cap)),
            )
        except Exception:
            pass


class CargaListView(LoginRequiredMixin, ListView):
	model = Carga
	template_name = 'fretes/carga_list.html'
	context_object_name = 'cargas'
	paginate_by = 15

	def get_queryset(self):
		queryset = super().get_queryset().select_related(
			'cliente', 'produto', 'fornecedor', 'caminhao', 'motorista', 'rota'
		)
		cliente = self.request.GET.get('cliente')
		produto = self.request.GET.get('produto')
		if cliente:
			queryset = queryset.filter(cliente__nome__icontains=cliente)
		if produto:
			queryset = queryset.filter(produto__nome__icontains=produto)
		return queryset


class CargaCreateView(LoginRequiredMixin, CreateView):
	model = Carga
	form_class = CargaForm
	template_name = 'fretes/carga_form.html'
	success_url = reverse_lazy('fretes:carga-list')

	def form_valid(self, form):
		response = super().form_valid(form)
		dados = self.request.POST.get('compartimentos_json', '')
		if dados and self.object.caminhao_id:
			_salvar_compartimentos(self.object.caminhao, dados)
		return response


class CargaUpdateView(LoginRequiredMixin, UpdateView):
	model = Carga
	form_class = CargaForm
	template_name = 'fretes/carga_form.html'
	success_url = reverse_lazy('fretes:carga-list')

	def form_valid(self, form):
		response = super().form_valid(form)
		dados = self.request.POST.get('compartimentos_json', '')
		if dados and self.object.caminhao_id:
			_salvar_compartimentos(self.object.caminhao, dados)
		return response
