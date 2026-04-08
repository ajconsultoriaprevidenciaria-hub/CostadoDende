from django.contrib import admin

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


class CompartimentoInline(admin.TabularInline):
	model = Compartimento
	extra = 1


@admin.register(Caminhao)
class CaminhaoAdmin(admin.ModelAdmin):
	list_display = ('placa', 'motorista_principal', 'local_carregamento', 'numero_compartimentos', 'capacidade_total_litros', 'ativo')
	list_filter = ('ativo', 'local_carregamento')
	search_fields = ('placa', 'motorista_principal__nome')
	inlines = [CompartimentoInline]


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
