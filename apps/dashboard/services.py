# Updated: fixed volume_por_posto query
from datetime import date, datetime
from decimal import Decimal

import plotly.express as px
import plotly.graph_objects as go
from django.db.models import Avg, Count, Sum

from apps.fretes.models import Carga, Cliente, Fornecedor, LocalCarregamento, Motorista, Produto, Rota


COLORWAY = ['#0f766e', '#f59e0b', '#1d4ed8', '#7c3aed', '#dc2626']


def _parse_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, '%Y-%m-%d').date()
    except ValueError:
        return None


def _empty_chart(title):
    fig = go.Figure()
    fig.update_layout(
        title=title,
        template='plotly_white',
        height=380,
        annotations=[
            {
                'text': 'Sem dados para o filtro selecionado',
                'xref': 'paper',
                'yref': 'paper',
                'showarrow': False,
                'font': {'size': 16},
                'x': 0.5,
                'y': 0.5,
            }
        ],
    )
    return fig.to_html(full_html=False, include_plotlyjs=False)


def _figure_to_html(fig):
    fig.update_layout(template='plotly_white', colorway=COLORWAY, height=380, margin=dict(l=20, r=20, t=60, b=20))
    return fig.to_html(full_html=False, include_plotlyjs=False)


def get_filtered_cargas(params):
    queryset = Carga.objects.select_related('cliente', 'produto', 'fornecedor', 'rota')

    data_inicial = _parse_date(params.get('data_inicial'))
    data_final = _parse_date(params.get('data_final'))
    cliente_id = params.get('cliente')
    produto_id = params.get('produto')
    fornecedor_id = params.get('fornecedor')
    rota_id = params.get('rota')

    if data_inicial:
        queryset = queryset.filter(data_carga__gte=data_inicial)
    if data_final:
        queryset = queryset.filter(data_carga__lte=data_final)
    if cliente_id:
        queryset = queryset.filter(cliente_id=cliente_id)
    if produto_id:
        queryset = queryset.filter(produto_id=produto_id)
    if fornecedor_id:
        queryset = queryset.filter(fornecedor_id=fornecedor_id)
    if rota_id:
        queryset = queryset.filter(rota_id=rota_id)

    return queryset, {
        'data_inicial': data_inicial or '',
        'data_final': data_final or '',
        'cliente': cliente_id or '',
        'produto': produto_id or '',
        'fornecedor': fornecedor_id or '',
        'rota': rota_id or '',
    }


def build_dashboard_context(params):
    queryset, filtros = get_filtered_cargas(params)

    viagens_por_caminhao = list(
        queryset.values('caminhao__placa').annotate(viagens=Count('id')).order_by('-viagens', 'caminhao__placa')
    )
    viagens_por_motorista = list(
        queryset.values('motorista__nome').annotate(viagens=Count('id')).order_by('-viagens', 'motorista__nome')
    )

    metricas = queryset.aggregate(
        total_litros=Sum('litros'),
        total_frete=Sum('valor_total_frete'),
        frete_medio=Avg('valor_frete_litro'),
        quantidade_cargas=Count('id'),
    )

    cliente_produto = list(
        queryset.values('cliente__nome', 'produto__nome').annotate(total_litros=Sum('litros')).order_by('cliente__nome', 'produto__nome')
    )
    fornecedor_totais = list(
        queryset.values('fornecedor__nome').annotate(total_frete=Sum('valor_total_frete')).order_by('-total_frete')
    )
    fornecedor_litros = list(
        queryset.values('fornecedor__nome').annotate(total_litros=Sum('litros')).order_by('-total_litros')
    )
    frete_medio_produto = list(
        queryset.values('produto__nome').annotate(frete_medio=Avg('valor_frete_litro')).order_by('-frete_medio')
    )
    volume_por_posto = list(
        queryset.values('caminhao__local_carregamento__nome').annotate(total_litros=Sum('litros')).order_by('-total_litros')
    )
    tabela_relatorio = list(
        queryset.values('cliente__nome', 'produto__nome', 'fornecedor__nome').annotate(
            litros=Sum('litros'),
            frete_total=Sum('valor_total_frete'),
            frete_medio=Avg('valor_frete_litro'),
            cargas=Count('id'),
        ).order_by('cliente__nome', 'produto__nome', 'fornecedor__nome')
    )

    if cliente_produto:
        fig_cliente_produto = px.bar(
            cliente_produto,
            x='cliente__nome',
            y='total_litros',
            color='produto__nome',
            barmode='group',
            title='Carga por cliente x produto',
            labels={'cliente__nome': 'Cliente', 'total_litros': 'Litros', 'produto__nome': 'Produto'},
        )
        grafico_cliente_produto = _figure_to_html(fig_cliente_produto)
    else:
        grafico_cliente_produto = _empty_chart('Carga por cliente x produto')

    if fornecedor_totais:
        fig_fornecedor = px.pie(
            fornecedor_totais,
            names='fornecedor__nome',
            values='total_frete',
            title='Participação do frete por fornecedor',
        )
        grafico_fornecedor = _figure_to_html(fig_fornecedor)
    else:
        grafico_fornecedor = _empty_chart('Participação do frete por fornecedor')

    if frete_medio_produto:
        fig_frete_medio = px.bar(
            frete_medio_produto,
            x='produto__nome',
            y='frete_medio',
            title='Valor médio do frete por produto',
            labels={'produto__nome': 'Produto', 'frete_medio': 'R$/litro'},
        )
        grafico_frete_medio = _figure_to_html(fig_frete_medio)
    else:
        grafico_frete_medio = _empty_chart('Valor médio do frete por produto')

    if volume_por_posto:
        fig_volume_posto = px.bar(
            volume_por_posto,
            x='caminhao__local_carregamento__nome',
            y='total_litros',
            title='Volume de carregamento por posto',
            labels={'caminhao__local_carregamento__nome': 'Posto', 'total_litros': 'Litros'},
        )
        grafico_volume_posto = _figure_to_html(fig_volume_posto)
    else:
        grafico_volume_posto = _empty_chart('Volume de carregamento por posto')

    if fornecedor_litros:
        fig_volume_fornecedor = px.bar(
            fornecedor_litros,
            x='fornecedor__nome',
            y='total_litros',
            title='Volume carregado por fornecedor',
            labels={'fornecedor__nome': 'Fornecedor', 'total_litros': 'Litros'},
        )
        grafico_volume_fornecedor = _figure_to_html(fig_volume_fornecedor)
    else:
        grafico_volume_fornecedor = _empty_chart('Volume carregado por fornecedor')

    return {
        'filtros': filtros,
        'clientes': Cliente.objects.filter(ativo=True).order_by('nome'),
        'produtos': Produto.objects.filter(ativo=True).order_by('nome'),
        'fornecedores': Fornecedor.objects.filter(ativo=True).order_by('nome'),
        'rotas': Rota.objects.filter(ativo=True).order_by('nome'),
        'total_litros': metricas['total_litros'] or Decimal('0.00'),
        'total_frete': metricas['total_frete'] or Decimal('0.00'),
        'frete_medio': metricas['frete_medio'] or Decimal('0.00'),
        'quantidade_cargas': metricas['quantidade_cargas'] or 0,
        'total_motoristas': Motorista.objects.filter(ativo=True).count(),
        'total_postos_cadastrados': LocalCarregamento.objects.filter(ativo=True).count(),
        'viagens_por_caminhao': viagens_por_caminhao,
        'viagens_por_motorista': viagens_por_motorista,
        'top_frete_medio_produtos': frete_medio_produto[:3],
        'top_postos_volume': volume_por_posto[:3],
        'grafico_cliente_produto': grafico_cliente_produto,
        'grafico_fornecedor': grafico_fornecedor,
        'grafico_frete_medio': grafico_frete_medio,
        'grafico_volume_posto': grafico_volume_posto,
        'grafico_volume_fornecedor': grafico_volume_fornecedor,
        'tabela_relatorio': tabela_relatorio,
        'hoje': date.today(),
    }
