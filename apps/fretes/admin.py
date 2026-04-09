from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse

from .models import (
	Caminhao,
	Carga,
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


@admin.register(Caminhao)
class CaminhaoAdmin(admin.ModelAdmin):
	list_display = ('placa_mercosul', 'motorista_principal', 'local_carregamento', 'numero_compartimentos', 'capacidade_total_litros', 'ativo', 'acoes')
	list_filter = ('ativo', 'local_carregamento')
	search_fields = ('placa', 'motorista_principal__nome')
	inlines = [CompartimentoInline]

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


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
	list_display = ('nome', 'documento', 'cidade', 'uf', 'ativo')
	list_filter = ('ativo', 'uf')
	search_fields = ('nome', 'documento', 'nome_fantasia')


@admin.register(Motorista)
class MotoristaAdmin(admin.ModelAdmin):
	list_display = ('nome', 'cpf', 'cnh', 'telefone', 'ativo')
	list_filter = ('ativo',)
	search_fields = ('nome', 'cpf', 'cnh')


@admin.register(LocalCarregamento)
class LocalCarregamentoAdmin(admin.ModelAdmin):
	list_display = ('nome', 'cidade', 'uf', 'ativo')
	list_filter = ('ativo', 'uf')
	search_fields = ('nome', 'cidade')


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
	list_display = ('nome', 'ativo')
	list_filter = ('ativo',)
	search_fields = ('nome',)


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
	list_display = ('nome', 'documento', 'cidade', 'uf', 'ativo')
	list_filter = ('ativo', 'uf')
	search_fields = ('nome', 'documento')


@admin.register(Rota)
class RotaAdmin(admin.ModelAdmin):
	list_display = ('nome', 'origem', 'destino', 'distancia_km', 'ativo')
	list_filter = ('ativo',)
	search_fields = ('nome', 'origem', 'destino')


@admin.register(TabelaFrete)
class TabelaFreteAdmin(admin.ModelAdmin):
	list_display = ('cliente', 'produto', 'rota', 'valor_por_litro', 'vigencia_inicio', 'vigencia_fim', 'ativo')
	list_filter = ('ativo', 'cliente', 'produto', 'rota')
	search_fields = ('cliente__nome', 'produto__nome', 'rota__nome')
	date_hierarchy = 'vigencia_inicio'


@admin.register(Carga)
class CargaAdmin(admin.ModelAdmin):
	list_display = (
		'data_carga',
		'cliente',
		'produto',
		'fornecedor',
		'caminhao',
		'litros',
		'valor_frete_litro',
		'valor_total_frete',
	)
	list_filter = ('data_carga', 'cliente', 'produto', 'fornecedor', 'rota')
	search_fields = ('cliente__nome', 'fornecedor__nome', 'caminhao__placa', 'numero_documento')
	autocomplete_fields = ('cliente', 'fornecedor', 'produto', 'caminhao', 'motorista', 'rota')
	date_hierarchy = 'data_carga'
