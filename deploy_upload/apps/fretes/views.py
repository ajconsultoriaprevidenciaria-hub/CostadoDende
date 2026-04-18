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
from .models import CargaCompartimento


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


@login_required
def carga_selecoes_json(request, pk):
	selecoes = list(
		CargaCompartimento.objects
		.filter(carga_id=pk)
		.select_related('compartimento', 'produto', 'cliente')
		.order_by('compartimento__numero')
	)
	result = []
	for s in selecoes:
		result.append({
			'compartimento_id': s.compartimento_id,
			'produto_id': s.produto_id,
			'cliente_id': s.cliente_id,
			'cliente_nome': s.cliente.nome if s.cliente_id else '',
		})
	return JsonResponse({'selecoes': result})


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
		placa = self.request.GET.get('placa')
		data_inicio = self.request.GET.get('data_inicio')
		data_fim = self.request.GET.get('data_fim')
		produto = self.request.GET.get('produto')
		if cliente:
			queryset = queryset.filter(cliente__nome__icontains=cliente)
		if placa:
			queryset = queryset.filter(caminhao__placa__icontains=placa)
		if data_inicio:
			queryset = queryset.filter(data_carga__gte=data_inicio)
		if data_fim:
			queryset = queryset.filter(data_carga__lte=data_fim)
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
def rota_info(request, pk):
	"""Retorna dados da rota (origem) para uso no formulário de Carga."""
	from .models import Rota
	try:
		rota = Rota.objects.get(pk=pk)
	except Rota.DoesNotExist:
		return JsonResponse({'error': 'Rota não encontrada'}, status=404)
	return JsonResponse({
		'origem': rota.origem,
		'distancia_km': float(rota.distancia_km) if rota.distancia_km else None,
		'tempo_total_min': rota.tempo_total_min,
	})


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
	"""Calcula distância e tempo total da rota, otimizando a ordem das paradas."""
	origem = request.GET.get('origem', '')
	destino = request.GET.get('destino', '')
	parada_ids = [int(x) for x in request.GET.getlist('parada_id') if x.strip()]
	click_lat = request.GET.get('lat', '')
	click_lng = request.GET.get('lng', '')

	origem_coords = ORIGENS_COORDS.get(origem)
	if not origem_coords:
		return JsonResponse({'error': 'Origem inválida'}, status=400)

	if not destino and not (click_lat and click_lng) and not parada_ids:
		return JsonResponse({'error': 'Informe o destino ou selecione paradas'}, status=400)

	def geocode_cidade(nome_local):
		parts = nome_local.replace(' ', '').split('/')
		cidade = parts[0] if parts else nome_local
		uf = parts[1] if len(parts) > 1 else ''
		search_q = f'{cidade}, {uf}, Brasil' if uf else f'{cidade}, Brasil'
		encoded = urllib.parse.quote(search_q)
		geo_url = (
			f'https://nominatim.openstreetmap.org/search?'
			f'q={encoded}&format=json&limit=1&countrycodes=br'
			f'&featuretype=city'
		)
		req = urllib.request.Request(geo_url, headers={'User-Agent': 'CostaDoDende/1.0'})
		with urllib.request.urlopen(req, timeout=8) as resp:
			geo_data = json.loads(resp.read().decode())
		if not geo_data:
			geo_url2 = (
				f'https://nominatim.openstreetmap.org/search?'
				f'q={encoded}&format=json&limit=1&countrycodes=br'
			)
			req2 = urllib.request.Request(geo_url2, headers={'User-Agent': 'CostaDoDende/1.0'})
			with urllib.request.urlopen(req2, timeout=8) as resp2:
				geo_data = json.loads(resp2.read().decode())
		if not geo_data:
			raise ValueError(f'Local não encontrado: {nome_local}')
		return float(geo_data[0]['lat']), float(geo_data[0]['lon'])

	try:
		o_lat, o_lng = origem_coords
		pontos = [{'nome': origem, 'lat': o_lat, 'lng': o_lng}]

		# Paradas a partir de clientes selecionados
		if parada_ids:
			from .models import Cliente
			clientes = Cliente.objects.filter(pk__in=parada_ids)
			cli_map = {c.pk: c for c in clientes}
			for pid in parada_ids:
				cli = cli_map.get(pid)
				if cli and cli.cidade:
					local = f'{cli.cidade}/{cli.uf}' if cli.uf else cli.cidade
					p_lat, p_lng = geocode_cidade(local)
					pontos.append({'nome': cli.nome, 'lat': p_lat, 'lng': p_lng, 'cidade': local})

		# Destino final
		has_destino = False
		if click_lat and click_lng:
			dest_lat = float(click_lat)
			dest_lng = float(click_lng)
			pontos.append({'nome': destino or 'Destino', 'lat': dest_lat, 'lng': dest_lng})
			has_destino = True
		elif destino:
			dest_lat, dest_lng = geocode_cidade(destino)
			pontos.append({'nome': destino, 'lat': dest_lat, 'lng': dest_lng})
			has_destino = True

		if len(pontos) < 2:
			return JsonResponse({'error': 'Informe ao menos um destino ou parada'}, status=400)

		coord_str = ';'.join(f"{p['lng']},{p['lat']}" for p in pontos)

		# Se há paradas intermediárias, usar OSRM trip para otimizar ordem
		if len(pontos) > 2 and parada_ids:
			trip_params = 'source=first&roundtrip=false&overview=full&geometries=geojson'
			if has_destino:
				trip_params += '&destination=last'
			osrm_url = (
				f'https://router.project-osrm.org/trip/v1/driving/{coord_str}?{trip_params}'
			)
			req = urllib.request.Request(osrm_url, headers={'User-Agent': 'CostaDoDende/1.0'})
			with urllib.request.urlopen(req, timeout=12) as resp:
				trip_data = json.loads(resp.read().decode())

			if trip_data.get('code') != 'Ok' or not trip_data.get('trips'):
				return JsonResponse({'error': 'Não foi possível otimizar a rota'}, status=404)

			trip = trip_data['trips'][0]
			waypoints_data = trip_data['waypoints']

			# Reconstruir ordem otimizada
			ordered_indices = sorted(
				range(len(pontos)),
				key=lambda i: waypoints_data[i]['waypoint_index']
			)
			pontos_otimizados = [pontos[i] for i in ordered_indices]

			dist_km = round(trip['distance'] / 1000, 2)
			tempo_total_min = int(round(trip.get('duration', 0) / 60))
			coords = trip['geometry']['coordinates']
		else:
			# Rota simples sem otimização
			osrm_url = (
				f'https://router.project-osrm.org/route/v1/driving/{coord_str}'
				f'?overview=full&geometries=geojson'
			)
			req = urllib.request.Request(osrm_url, headers={'User-Agent': 'CostaDoDende/1.0'})
			with urllib.request.urlopen(req, timeout=12) as resp:
				route_data = json.loads(resp.read().decode())

			if route_data.get('code') != 'Ok' or not route_data.get('routes'):
				return JsonResponse({'error': 'Não foi possível calcular rota'}, status=404)

			route = route_data['routes'][0]
			pontos_otimizados = pontos
			dist_km = round(route['distance'] / 1000, 2)
			tempo_total_min = int(round(route.get('duration', 0) / 60))
			coords = route['geometry']['coordinates']

		tempo_h = tempo_total_min // 60
		tempo_m = tempo_total_min % 60

		# Último ponto (destino final)
		dest_final = pontos_otimizados[-1]
		dest_lat = dest_final['lat']
		dest_lng = dest_final['lng']

		# Google Maps URL
		gmaps_params = {
			'api': '1',
			'origin': f"{pontos_otimizados[0]['lat']},{pontos_otimizados[0]['lng']}",
			'destination': f"{dest_lat},{dest_lng}",
			'travelmode': 'driving',
		}
		if len(pontos_otimizados) > 2:
			gmaps_params['waypoints'] = '|'.join(
				f"{p['lat']},{p['lng']}" for p in pontos_otimizados[1:-1]
			)
		gmaps_url = 'https://www.google.com/maps/dir/?' + urllib.parse.urlencode(gmaps_params)

		if len(coords) > 200:
			coords = coords[::max(1, len(coords)//200)] + [coords[-1]]

		# Ordem de entrega (apenas paradas, sem origem)
		ordem_entrega = []
		for i, p in enumerate(pontos_otimizados):
			if i == 0:
				continue  # pular origem
			ordem_entrega.append({'ordem': len(ordem_entrega) + 1, 'nome': p['nome'], 'lat': p['lat'], 'lng': p['lng']})

		return JsonResponse({
			'distancia_km': dist_km,
			'destino_lat': dest_lat,
			'destino_lng': dest_lng,
			'origem_lat': o_lat,
			'origem_lng': o_lng,
			'tempo_total_min': tempo_total_min,
			'tempo_total_h': tempo_h,
			'tempo_total_m': tempo_m,
			'gmaps_url': gmaps_url,
			'origem_nome': origem,
			'destino_nome': dest_final['nome'],
			'trajeto_nomes': [p['nome'] for p in pontos_otimizados],
			'ordem_entrega': ordem_entrega,
			'rota_coords': coords,
		})
	except ValueError as e:
		return JsonResponse({'error': str(e)}, status=404)
	except Exception as e:
		return JsonResponse({'error': f'Erro ao calcular rota: {e}'}, status=500)


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
