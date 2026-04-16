from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.utils.html import format_html
from django.urls import path, reverse
from django.shortcuts import get_object_or_404, render
from apps.motorista_portal.models import AbastecimentoViagem, ChecklistViagem
from apps.dashboard.services import build_dashboard_context

from .models import (
	Caminhao,
	CaminhaoDocumento,
	Carga,
	CargaCliente,
	CargaCompartimento,
	Cliente,
	Compartimento,
	Fornecedor,
	LocalCarregamento,
	Motorista,
	Produto,
	Rota,
	TabelaFrete,
)

admin.site.site_header = 'Costa do Dendê | Administração'
admin.site.site_title = 'Costa do Dendê'
admin.site.index_title = 'Painel administrativo de fretes'


_default_admin_index = admin.site.index


def dashboard_admin_index(request, extra_context=None):
	extra_context = extra_context or {}
	extra_context.update(build_dashboard_context(request.GET))
	return _default_admin_index(request, extra_context=extra_context)


admin.site.index = dashboard_admin_index


@admin.register(Compartimento)
class CompartimentoAdmin(admin.ModelAdmin):
	list_display = ('caminhao', 'numero', 'capacidade_litros')
	list_filter = ('caminhao',)


class CompartimentoInline(admin.TabularInline):
	model = Compartimento
	fields = ('numero', 'capacidade_litros')
	extra = 1
	can_delete = True
	show_change_link = True


class CaminhaoDocumentoInline(admin.StackedInline):
	model = CaminhaoDocumento
	fields = ('tipo', 'descricao', 'arquivo', 'data_validade', 'observacoes')
	extra = 1
	show_change_link = True


@admin.register(Caminhao)
class CaminhaoAdmin(admin.ModelAdmin):
	list_display = ('placa_mercosul', 'motorista_principal', 'local_carregamento', 'numero_compartimentos', 'capacidade_total_litros', 'ativo', 'acoes')
	list_filter = ('ativo', 'local_carregamento')
	search_fields = ('placa', 'motorista_principal__nome')
	inlines = [CompartimentoInline, CaminhaoDocumentoInline]

	class Media:
		js = ('admin/js/placa_mercosul.js',)

	@admin.display(description='Placa', ordering='placa')
	def placa_mercosul(self, obj):
		p = obj.placa.upper().replace('-', '').replace(' ', '')
		if len(p) == 7:
			formatted = f'{p[:3]}{p[3]}{p[4:]}'
			return format_html(
				'<span style="font-family:monospace;font-weight:800;font-size:.85rem;'
				'background:#0d1929;border:2px solid #3b82f6;border-radius:6px;padding:3px 8px;'
				'display:inline-block;letter-spacing:.08em;color:#fff;text-align:center;'
				'border-top:14px solid #3b82f6;position:relative;">'
				'<span style="position:absolute;top:-13px;left:0;right:0;font-size:.45rem;'
				'color:#fff;font-weight:700;letter-spacing:.15em;">BRASIL</span>'
				'{}</span>', formatted)
		return obj.placa

	@admin.display(description='Ações')
	def acoes(self, obj):
		edit_url = reverse('admin:fretes_caminhao_change', args=[obj.pk])
		delete_url = reverse('admin:fretes_caminhao_delete', args=[obj.pk])
		docs_url = reverse('admin:fretes_caminhaodocumento_changelist') + f'?caminhao__id__exact={obj.pk}'
		return format_html(
			'<a href="{}" style="background:var(--panel);color:var(--primary);border:1px solid var(--border);'
			'border-radius:6px;padding:4px 10px;font-size:.72rem;font-weight:700;text-decoration:none;'
			'margin-right:5px;display:inline-block;transition:all .18s;"'
			' onmouseover="this.style.background=\'var(--primary)\';this.style.color=\'#070d1a\'"'
			' onmouseout="this.style.background=\'var(--panel)\';this.style.color=\'var(--primary)\'">'
			'✏️ Editar</a>'
			'<a href="{}" style="background:rgba(59,130,246,.1);color:#3b82f6;border:1px solid rgba(59,130,246,.25);'
			'border-radius:6px;padding:4px 10px;font-size:.72rem;font-weight:700;text-decoration:none;'
			'display:inline-block;transition:all .18s;margin-right:5px;'
			' onmouseover="this.style.background=\'#3b82f6\';this.style.color=\'#fff\'"'
			' onmouseout="this.style.background=\'rgba(59,130,246,.1)\';this.style.color=\'#3b82f6\'">'
			'<span class="action-icon">�</span></a>'
			'<a href="{}" style="background:rgba(239,68,68,.1);color:#ef4444;border:1px solid rgba(239,68,68,.25);'
			'border-radius:6px;padding:4px 10px;font-size:.72rem;font-weight:700;text-decoration:none;'
			'display:inline-block;transition:all .18s;'
			' onmouseover="this.style.background=\'#ef4444\';this.style.color=\'#fff\'"'
			' onmouseout="this.style.background=\'rgba(239,68,68,.1)\';this.style.color=\'#ef4444\'">'
			'🗑️ Excluir</a>',
			edit_url, docs_url, delete_url
		)


@admin.register(CaminhaoDocumento)
class CaminhaoDocumentoAdmin(admin.ModelAdmin):
	list_display = ('caminhao', 'tipo', 'descricao', 'arquivo_link', 'data_validade', 'ativo')
	list_filter = ('tipo', 'data_validade', 'ativo')
	search_fields = ('caminhao__placa', 'descricao')
	search_help_text = 'Pesquise pela placa do caminhão ou descrição do documento'
	autocomplete_fields = ('caminhao',)
	ordering = ('caminhao__placa', 'tipo')

	@admin.display(description='Arquivo')
	def arquivo_link(self, obj):
		if obj.arquivo:
			return format_html(
				'<a href="{}" download style="display:inline-flex;align-items:center;gap:6px;'
				'background:rgba(16,185,129,.12);color:#10b981;border:1px solid rgba(16,185,129,.25);'
				'border-radius:6px;padding:4px 10px;font-size:.78rem;font-weight:700;text-decoration:none;'
				'transition:all .18s;" title="Baixar documento">'
				'📥 Baixar</a>', obj.arquivo.url)
		return '-'


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
	list_display = ('nome', 'documento', 'cidade', 'uf', 'ativo')
	list_filter = ('ativo', 'uf')
	search_fields = ('nome', 'documento', 'nome_fantasia')


@admin.register(Motorista)
class MotoristaAdmin(admin.ModelAdmin):
	list_display = ('nome', 'cpf', 'cnh', 'telefone', 'user', 'ativo', 'acoes')
	list_filter = ('ativo',)
	search_fields = ('nome', 'cpf', 'cnh')
	list_editable = ('ativo',)
	raw_id_fields = ('user',)

	@admin.display(description='Ações')
	def acoes(self, obj):
		edit_url = reverse('admin:fretes_motorista_change', args=[obj.pk])
		delete_url = reverse('admin:fretes_motorista_delete', args=[obj.pk])
		return format_html(
			'<a href="{}" style="background:var(--panel);color:var(--primary);border:1px solid var(--border);'
			'border-radius:6px;padding:4px 10px;font-size:.72rem;font-weight:700;text-decoration:none;'
			'margin-right:5px;display:inline-block;transition:all .18s;"'
			' onmouseover="this.style.background=\'var(--primary)\';this.style.color=\'#070d1a\'"'
			' onmouseout="this.style.background=\'var(--panel)\';this.style.color=\'var(--primary)\'">'
			'✏️ Editar</a>'
			'<a href="{}" style="background:rgba(239,68,68,.1);color:#ef4444;border:1px solid rgba(239,68,68,.25);'
			'border-radius:6px;padding:4px 10px;font-size:.72rem;font-weight:700;text-decoration:none;'
			'display:inline-block;transition:all .18s;"'
			' onmouseover="this.style.background=\'#ef4444\';this.style.color=\'#fff\'"'
			' onmouseout="this.style.background=\'rgba(239,68,68,.1)\';this.style.color=\'#ef4444\'">'
			'🗑️ Excluir</a>',
			edit_url, delete_url
		)


@admin.register(LocalCarregamento)
class LocalCarregamentoAdmin(admin.ModelAdmin):
	list_display = ('nome', 'cidade', 'uf', 'ativo')
	list_filter = ('ativo', 'uf')
	search_fields = ('nome', 'cidade')


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
	list_display = ('nome', 'ativo', 'acoes')
	list_filter = ('ativo',)
	search_fields = ('nome',)
	list_editable = ('ativo',)

	@admin.display(description='Ações')
	def acoes(self, obj):
		edit_url = reverse('admin:fretes_produto_change', args=[obj.pk])
		delete_url = reverse('admin:fretes_produto_delete', args=[obj.pk])
		return format_html(
			'<a href="{}" style="background:var(--panel);color:var(--primary);border:1px solid var(--border);'
			'border-radius:6px;padding:4px 10px;font-size:.72rem;font-weight:700;text-decoration:none;'
			'margin-right:5px;display:inline-block;transition:all .18s;"'
			' onmouseover="this.style.background=\'var(--primary)\';this.style.color=\'#070d1a\'"'
			' onmouseout="this.style.background=\'var(--panel)\';this.style.color=\'var(--primary)\'">'
			'✏️ Editar</a>'
			'<a href="{}" style="background:rgba(239,68,68,.1);color:#ef4444;border:1px solid rgba(239,68,68,.25);'
			'border-radius:6px;padding:4px 10px;font-size:.72rem;font-weight:700;text-decoration:none;'
			'display:inline-block;transition:all .18s;"'
			' onmouseover="this.style.background=\'#ef4444\';this.style.color=\'#fff\'"'
			' onmouseout="this.style.background=\'rgba(239,68,68,.1)\';this.style.color=\'#ef4444\'">'
			'🗑️ Excluir</a>',
			edit_url, delete_url
		)


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
	list_display = ('nome', 'documento', 'cidade', 'uf', 'ativo')
	list_filter = ('ativo', 'uf')
	search_fields = ('nome', 'documento')


@admin.register(Rota)
class RotaAdmin(admin.ModelAdmin):
	list_display = ('nome', 'origem', 'destino', 'distancia_km', 'ativo', 'acoes')
	list_filter = ('ativo', 'origem')
	search_fields = ('nome', 'origem', 'destino')
	readonly_fields = ('destino_lat', 'destino_lng')
	fieldsets = (
		(None, {'fields': ('nome', 'origem', 'destino', 'distancia_km', 'ativo')}),
		('Coordenadas (preenchido automaticamente)', {
			'classes': ('collapse',),
			'fields': ('destino_lat', 'destino_lng'),
		}),
	)

	class Media:
		css = {'all': ('https://unpkg.com/leaflet@1.9.4/dist/leaflet.css',)}
		js = (
			'https://unpkg.com/leaflet@1.9.4/dist/leaflet.js',
			'admin/js/rota_destino.js',
		)

	@admin.display(description='Ações')
	def acoes(self, obj):
		edit_url = reverse('admin:fretes_rota_change', args=[obj.pk])
		delete_url = reverse('admin:fretes_rota_delete', args=[obj.pk])
		return format_html(
			'<a href="{}" style="background:var(--panel);color:var(--primary);border:1px solid var(--border);'
			'border-radius:6px;padding:4px 10px;font-size:.72rem;font-weight:700;text-decoration:none;'
			'margin-right:5px;display:inline-block;transition:all .18s;"'
			' onmouseover="this.style.background=\'var(--primary)\';this.style.color=\'#070d1a\'"'
			' onmouseout="this.style.background=\'var(--panel)\';this.style.color=\'var(--primary)\'">'
			'✏️ Editar</a>'
			'<a href="{}" style="background:rgba(239,68,68,.1);color:#ef4444;border:1px solid rgba(239,68,68,.25);'
			'border-radius:6px;padding:4px 10px;font-size:.72rem;font-weight:700;text-decoration:none;'
			'display:inline-block;transition:all .18s;"'
			' onmouseover="this.style.background=\'#ef4444\';this.style.color=\'#fff\'"'
			' onmouseout="this.style.background=\'rgba(239,68,68,.1)\';this.style.color=\'#ef4444\'">'
			'🗑️ Excluir</a>',
			edit_url, delete_url
		)


@admin.register(TabelaFrete)
class TabelaFreteAdmin(admin.ModelAdmin):
	list_display = ('cliente', 'produto', 'rota', 'valor_por_litro', 'vigencia_inicio', 'vigencia_fim', 'ativo')
	list_filter = ('ativo', 'cliente', 'produto', 'rota')
	search_fields = ('cliente__nome', 'produto__nome', 'rota__nome')
	date_hierarchy = 'vigencia_inicio'


class CargaClienteInlineFormSet(BaseInlineFormSet):
	def add_fields(self, form, index):
		super().add_fields(form, index)
		if index is None:
			return
		if 'ordem' in form.fields and not form.instance.pk:
			form.initial.setdefault('ordem', index + 2)


class CargaClienteInline(admin.StackedInline):
	model = CargaCliente
	formset = CargaClienteInlineFormSet
	extra = 6
	max_num = 6
	fields = ('ordem', 'cliente')
	autocomplete_fields = ('cliente',)
	verbose_name = 'Cliente adicional'
	verbose_name_plural = 'Clientes 2 a 7'


class CargaCompartimentoInline(admin.StackedInline):
	model = CargaCompartimento
	extra = 0
	fields = ('compartimento', 'produto')


@admin.register(Carga)
class CargaAdmin(admin.ModelAdmin):
	change_list_template = 'admin/fretes/carga/change_list.html'

	list_display = (
		'data_carga_fmt',
		'cliente',
		'motorista',
		'rota',
		'caminhao',
		'litros_fmt',
		'frete_litro_fmt',
		'total_frete_fmt',
		'acoes',
	)
	list_filter = ()
	search_fields = ('cliente__nome', 'fornecedor__nome', 'caminhao__placa', 'numero_documento')
	exclude = ('produto',)
	autocomplete_fields = ('cliente', 'fornecedor', 'caminhao', 'motorista', 'rota')
	inlines = [CargaClienteInline, CargaCompartimentoInline]
	date_hierarchy = 'data_carga'

	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
		if db_field.name == 'cliente':
			formfield.label = 'Cliente 1'
		return formfield

	def get_queryset(self, request):
		queryset = super().get_queryset(request)
		placa = (request.GET.get('placa') or '').strip()
		cliente_id = (request.GET.get('cliente_id') or '').strip()
		data_inicio = (request.GET.get('data_inicio') or '').strip()
		data_fim = (request.GET.get('data_fim') or '').strip()

		if placa:
			queryset = queryset.filter(caminhao__placa__icontains=placa)
		if cliente_id:
			queryset = queryset.filter(cliente_id=cliente_id)
		if data_inicio:
			queryset = queryset.filter(data_carga__gte=data_inicio)
		if data_fim:
			queryset = queryset.filter(data_carga__lte=data_fim)

		return queryset

	def save_related(self, request, form, formsets, change):
		super().save_related(request, form, formsets, change)
		if change:
			return

		carga_principal = form.instance
		clientes_extras = list(
			carga_principal.clientes_adicionais.select_related('cliente').order_by('ordem')
		)
		if not clientes_extras:
			return

		compartimentos = list(carga_principal.carga_compartimentos.all())

		for extra in clientes_extras:
			nova_carga = Carga.objects.create(
				data_carga=carga_principal.data_carga,
				cliente=extra.cliente,
				fornecedor=carga_principal.fornecedor,
				produto=carga_principal.produto,
				caminhao=carga_principal.caminhao,
				motorista=carga_principal.motorista,
				rota=carga_principal.rota,
				litros=carga_principal.litros,
				valor_frete_litro=carga_principal.valor_frete_litro,
				valor_total_frete=carga_principal.valor_total_frete,
				numero_documento=carga_principal.numero_documento,
				observacoes=carga_principal.observacoes,
			)

			if compartimentos:
				CargaCompartimento.objects.bulk_create([
					CargaCompartimento(
						carga=nova_carga,
						compartimento=item.compartimento,
						produto=item.produto,
					)
					for item in compartimentos
				])

		# Após gerar as cargas individualizadas, limpa os clientes extras da carga principal.
		carga_principal.clientes_adicionais.all().delete()

	def changelist_view(self, request, extra_context=None):
		response = super().changelist_view(request, extra_context=extra_context)
		if not hasattr(response, 'context_data') or 'cl' not in response.context_data:
			return response

		response.context_data['clientes_filtro'] = Cliente.objects.filter(ativo=True).order_by('nome')

		base_qs = response.context_data['cl'].queryset
		cargas_concluidas_ids = AbastecimentoViagem.objects.filter(
			despesa__carga__in=base_qs,
			despesa__tipo='abastecimento',
			foto_cupom__isnull=False,
		).exclude(
			foto_cupom='',
		).values_list('despesa__carga_id', flat=True)

		cargas_concluidas = base_qs.filter(
			checklists__concluido=True,
			id__in=cargas_concluidas_ids,
		).distinct().select_related(
			'cliente', 'motorista', 'rota', 'caminhao'
		)

		response.context_data['cargas_concluidas'] = cargas_concluidas
		response.context_data['qtd_cargas_concluidas'] = cargas_concluidas.count()
		return response

	@admin.display(description='DATA DA CARGA', ordering='data_carga')
	def data_carga_fmt(self, obj):
		return obj.data_carga.strftime('%d/%m/%Y')

	@admin.display(description='Litros', ordering='litros')
	def litros_fmt(self, obj):
		val = f"{int(obj.litros):,}".replace(',', '.')
		return f"{val} L"

	@admin.display(description='R$/Litro', ordering='valor_frete_litro')
	def frete_litro_fmt(self, obj):
		if obj.valor_frete_litro is None:
			return '-'
		return f"R$ {obj.valor_frete_litro:.4f}"

	@admin.display(description='Total Frete', ordering='valor_total_frete')
	def total_frete_fmt(self, obj):
		if obj.valor_total_frete is None:
			return '-'
		val = f"{obj.valor_total_frete:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
		return f"R$ {val}"

	@admin.display(description='Ações')
	def acoes(self, obj):
		edit_url = reverse('admin:fretes_carga_change', args=[obj.pk])
		delete_url = reverse('admin:fretes_carga_delete', args=[obj.pk])
		return format_html(
			'<a href="{}" style="background:var(--panel);color:var(--primary);border:1px solid var(--border);'
			'border-radius:6px;padding:4px 10px;font-size:.72rem;font-weight:700;text-decoration:none;'
			'margin-right:5px;display:inline-block;transition:all .18s;"'
			' onmouseover="this.style.background=\'var(--primary)\';this.style.color=\'#070d1a\'"'
			' onmouseout="this.style.background=\'var(--panel)\';this.style.color=\'var(--primary)\'">'
			'✏️ Editar</a>'
			'<a href="{}" style="background:rgba(239,68,68,.1);color:#ef4444;border:1px solid rgba(239,68,68,.25);'
			'border-radius:6px;padding:4px 10px;font-size:.72rem;font-weight:700;text-decoration:none;'
			'display:inline-block;transition:all .18s;"'
			' onmouseover="this.style.background=\'#ef4444\';this.style.color=\'#fff\'"'
			' onmouseout="this.style.background=\'rgba(239,68,68,.1)\';this.style.color=\'#ef4444\'">'
			'🗑️ Excluir</a>',
			edit_url, delete_url
		)

	class Media:
		js = ('admin/js/carga_compartimentos.js',)

	def get_urls(self):
		urls = super().get_urls()
		custom = [
			path(
				'<int:carga_pk>/info-viagem/',
				self.admin_site.admin_view(self.info_viagem_view),
				name='fretes_carga_info_viagem',
			),
		]
		return custom + urls

	def info_viagem_view(self, request, carga_pk):
		carga = get_object_or_404(Carga, pk=carga_pk)
		checklists = ChecklistViagem.objects.filter(
			carga=carga,
		).prefetch_related('itens').order_by('-data_hora')
		abastecimentos = AbastecimentoViagem.objects.filter(
			despesa__carga=carga,
		).select_related('despesa').order_by('-despesa__data')
		context = {
			**self.admin_site.each_context(request),
			'carga': carga,
			'checklists': checklists,
			'abastecimentos': abastecimentos,
			'title': f'Informações da Viagem — Carga #{carga.pk}',
			'opts': self.model._meta,
		}
		return render(request, 'admin/fretes/carga/info_viagem.html', context)
