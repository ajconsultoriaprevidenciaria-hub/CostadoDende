import json
import urllib.request
import urllib.parse
from decimal import Decimal

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import CargaForm
from .models import Caminhao, Carga, Compartimento, Produto


@login_required
def caminhao_compartimentos_json(request, pk):
    try:
        caminhao = Caminhao.objects.get(pk=pk)
    except Caminhao.DoesNotExist:
        return JsonResponse({'compartimentos': []})
    compartimentos = list(
        caminhao.compartimentos.order_by('numero').values('id', 'numero', 'capacidade_litros')
    )
    for c in compartimentos:
        c['capacidade_litros'] = float(c['capacidade_litros'])
    return JsonResponse({'compartimentos': compartimentos})


@login_required
def produtos_json(request):
    produtos = list(Produto.objects.filter(ativo=True).order_by('nome').values('id', 'nome'))
    return JsonResponse({'produtos': produtos})


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


class CargaDeleteView(LoginRequiredMixin, DeleteView):
	model = Carga
	template_name = 'fretes/carga_confirm_delete.html'
	success_url = reverse_lazy('fretes:carga-list')


# ══ APIs para o formulário de Rota ════════════════════════════════

ORIGENS_COORDS = {
	'Candeias/BA': (-12.67218, -38.54737),
	'São Francisco do Conde/BA': (-12.62836, -38.67952),
	'Suape/PE': (-8.39356, -35.06017),
}


@staff_member_required
def buscar_cidades(request):
	"""Busca cidades brasileiras via API IBGE."""
	q = request.GET.get('q', '').strip()
	if len(q) < 2:
		return JsonResponse([], safe=False)
	try:
		url = 'https://servicodados.ibge.gov.br/api/v1/localidades/municipios?orderBy=nome'
		req = urllib.request.Request(url, headers={'User-Agent': 'CostaDoDende/1.0'})
		with urllib.request.urlopen(req, timeout=8) as resp:
			municipios = json.loads(resp.read().decode())
		q_lower = q.lower()
		resultados = []
		for m in municipios:
			nome = m['nome']
			uf = m['microrregiao']['mesorregiao']['UF']['sigla']
			if q_lower in nome.lower():
				resultados.append({'nome': f'{nome}/{uf}', 'id': m['id']})
			if len(resultados) >= 15:
				break
		return JsonResponse(resultados, safe=False)
	except Exception:
		return JsonResponse([], safe=False)


@staff_member_required
def calcular_distancia(request):
	"""Calcula distância via OSRM com geometria da rota para o mapa."""
	origem = request.GET.get('origem', '')
	destino = request.GET.get('destino', '')
	# Suporte a lat/lng por clique no mapa
	click_lat = request.GET.get('lat', '')
	click_lng = request.GET.get('lng', '')

	origem_coords = ORIGENS_COORDS.get(origem)
	if not origem_coords:
		return JsonResponse({'error': 'Origem inválida'}, status=400)

	if click_lat and click_lng:
		# Destino veio por clique no mapa
		dest_lat = float(click_lat)
		dest_lng = float(click_lng)
	else:
		# Geocodificar destino via Nominatim
		try:
			parts = destino.replace(' ', '').split('/')
			cidade = parts[0] if parts else destino
			uf = parts[1] if len(parts) > 1 else ''
			search_q = f'{cidade}, {uf}, Brasil' if uf else f'{cidade}, Brasil'
			dest_encoded = urllib.parse.quote(search_q)
			geo_url = (
				f'https://nominatim.openstreetmap.org/search?'
				f'q={dest_encoded}&format=json&limit=1&countrycodes=br'
				f'&featuretype=city'
			)
			req = urllib.request.Request(geo_url, headers={'User-Agent': 'CostaDoDende/1.0'})
			with urllib.request.urlopen(req, timeout=8) as resp:
				geo_data = json.loads(resp.read().decode())
			if not geo_data:
				geo_url2 = (
					f'https://nominatim.openstreetmap.org/search?'
					f'q={dest_encoded}&format=json&limit=1&countrycodes=br'
				)
				req2 = urllib.request.Request(geo_url2, headers={'User-Agent': 'CostaDoDende/1.0'})
				with urllib.request.urlopen(req2, timeout=8) as resp2:
					geo_data = json.loads(resp2.read().decode())
			if not geo_data:
				return JsonResponse({'error': 'Destino não encontrado'}, status=404)
			dest_lat = float(geo_data[0]['lat'])
			dest_lng = float(geo_data[0]['lon'])
		except Exception as e:
			return JsonResponse({'error': f'Erro ao geocodificar: {e}'}, status=500)

	# Calcular rota via OSRM com geometria
	try:
		o_lat, o_lng = origem_coords
		osrm_url = (
			f'https://router.project-osrm.org/route/v1/driving/'
			f'{o_lng},{o_lat};{dest_lng},{dest_lat}'
			f'?overview=full&geometries=geojson'
		)
		req = urllib.request.Request(osrm_url, headers={'User-Agent': 'CostaDoDende/1.0'})
		with urllib.request.urlopen(req, timeout=10) as resp:
			route_data = json.loads(resp.read().decode())
		if route_data.get('code') != 'Ok' or not route_data.get('routes'):
			return JsonResponse({'error': 'Não foi possível calcular rota'}, status=404)
		route = route_data['routes'][0]
		dist_km = round(route['distance'] / 1000, 2)
		previsao_min = round((dist_km / 80) * 60)
		previsao_h = previsao_min // 60
		previsao_m = previsao_min % 60
		gmaps_url = f'https://www.google.com/maps/dir/{o_lat},{o_lng}/{dest_lat},{dest_lng}'
		# Simplificar geometria para o frontend (cada 5º ponto)
		coords = route['geometry']['coordinates']
		if len(coords) > 200:
			coords = coords[::max(1, len(coords)//200)] + [coords[-1]]
		return JsonResponse({
			'distancia_km': dist_km,
			'destino_lat': dest_lat,
			'destino_lng': dest_lng,
			'origem_lat': o_lat,
			'origem_lng': o_lng,
			'previsao_viagem_min': previsao_min,
			'previsao_viagem_h': previsao_h,
			'previsao_viagem_m': previsao_m,
			'gmaps_url': gmaps_url,
			'origem_nome': origem,
			'destino_nome': destino,
			'rota_coords': coords,
		})
	except Exception as e:
		return JsonResponse({'error': f'Erro OSRM: {e}'}, status=500)


@staff_member_required
def reverse_geocode(request):
	"""Reverse geocode: lat/lng -> nome da cidade."""
	lat = request.GET.get('lat', '')
	lng = request.GET.get('lng', '')
	if not lat or not lng:
		return JsonResponse({'error': 'lat/lng required'}, status=400)
	try:
		geo_url = (
			f'https://nominatim.openstreetmap.org/reverse?'
			f'lat={lat}&lon={lng}&format=json&zoom=10&addressdetails=1'
		)
		req = urllib.request.Request(geo_url, headers={'User-Agent': 'CostaDoDende/1.0'})
		with urllib.request.urlopen(req, timeout=8) as resp:
			data = json.loads(resp.read().decode())
		addr = data.get('address', {})
		city = addr.get('city') or addr.get('town') or addr.get('municipality') or addr.get('village', '')
		state = addr.get('state', '')
		# Abreviar estado
		uf_map = {
			'Acre': 'AC', 'Alagoas': 'AL', 'Amapá': 'AP', 'Amazonas': 'AM',
			'Bahia': 'BA', 'Ceará': 'CE', 'Distrito Federal': 'DF',
			'Espírito Santo': 'ES', 'Goiás': 'GO', 'Maranhão': 'MA',
			'Mato Grosso': 'MT', 'Mato Grosso do Sul': 'MS',
			'Minas Gerais': 'MG', 'Pará': 'PA', 'Paraíba': 'PB',
			'Paraná': 'PR', 'Pernambuco': 'PE', 'Piauí': 'PI',
			'Rio de Janeiro': 'RJ', 'Rio Grande do Norte': 'RN',
			'Rio Grande do Sul': 'RS', 'Rondônia': 'RO', 'Roraima': 'RR',
			'Santa Catarina': 'SC', 'São Paulo': 'SP', 'Sergipe': 'SE',
			'Tocantins': 'TO',
		}
		uf = uf_map.get(state, state[:2].upper() if state else '')
		nome = f'{city}/{uf}' if city else data.get('display_name', '')
		return JsonResponse({'nome': nome, 'lat': float(lat), 'lng': float(lng)})
	except Exception as e:
		return JsonResponse({'error': str(e)}, status=500)
