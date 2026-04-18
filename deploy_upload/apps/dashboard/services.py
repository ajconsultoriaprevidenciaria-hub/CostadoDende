# Updated: fixed volume_por_posto query
from datetime import date, datetime
from decimal import Decimal

import plotly.express as px
import plotly.graph_objects as go
from django.db.models import Avg, Count, Sum

from apps.fretes.models import Carga, Cliente, Fornecedor, LocalCarregamento, Motorista, Produto, Rota
from apps.motorista_portal.models import AbastecimentoViagem


COLORWAY = ['#ff6b6b', '#00d9a6', '#f59e0b', '#a78bfa', '#3b82f6', '#f472b6', '#2dd4bf']

_DARK_LAYOUT = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    font=dict(family='Inter, system-ui, sans-serif', color='#e2e8f0', size=12),
    title_font=dict(size=15, color='#e2e8f0'),
    legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#94a3b8', size=11)),
    xaxis=dict(
        gridcolor='rgba(100,116,139,.12)', gridwidth=1,
        linecolor='rgba(100,116,139,.2)', linewidth=1,
        tickfont=dict(color='#94a3b8', size=11), title_font=dict(color='#94a3b8'),
    ),
    yaxis=dict(
        gridcolor='rgba(100,116,139,.12)', gridwidth=1,
        linecolor='rgba(100,116,139,.2)', linewidth=1,
        tickfont=dict(color='#94a3b8', size=11), title_font=dict(color='#94a3b8'),
    ),
)


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
        height=380,
        **_DARK_LAYOUT,
        annotations=[
            {
                'text': 'Sem dados para o filtro selecionado',
                'xref': 'paper',
                'yref': 'paper',
                'showarrow': False,
                'font': {'size': 14, 'color': '#64748b'},
                'x': 0.5,
                'y': 0.5,
            }
        ],
    )
    return fig.to_html(full_html=False, include_plotlyjs=False)


def _figure_to_html(fig):
    fig.update_layout(
        colorway=COLORWAY,
        height=380,
        margin=dict(l=20, r=20, t=50, b=20),
        bargap=0.25,
        **_DARK_LAYOUT,
    )
    return fig.to_html(full_html=False, include_plotlyjs=False)


def _hbar_to_html(fig, n_items):
    h = max(220, min(380, 50 + n_items * 45))
    fig.update_layout(
        colorway=COLORWAY,
        height=h,
        margin=dict(l=10, r=60, t=50, b=20),
        bargap=0.35,
        **_DARK_LAYOUT,
    )
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


def get_relatorio_abastecimentos(params):
    qs = AbastecimentoViagem.objects.select_related('despesa')

    data_inicial = _parse_date(params.get('data_inicial'))
    data_final = _parse_date(params.get('data_final'))

    if data_inicial:
        qs = qs.filter(despesa__data__gte=data_inicial)
    if data_final:
        qs = qs.filter(despesa__data__lte=data_final)

    return list(
        qs.values('posto').annotate(
            total_litros=Sum('litros'),
            total_abastecimentos=Count('id'),
            total_valor=Sum('despesa__valor'),
        ).order_by('-total_litros', 'posto')
    )


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
            title='Litros por Cliente × Produto',
            labels={'cliente__nome': '', 'total_litros': 'Litros', 'produto__nome': 'Produto'},
        )
        fig_cliente_produto.update_traces(
            marker_line_width=0, opacity=0.92,
            texttemplate='%{y:,.0f}', textposition='outside',
            textfont=dict(size=10, color='#94a3b8'),
        )
        grafico_cliente_produto = _figure_to_html(fig_cliente_produto)
    else:
        grafico_cliente_produto = _empty_chart('Litros por Cliente × Produto')

    if fornecedor_totais:
        fig_fornecedor = px.pie(
            fornecedor_totais,
            names='fornecedor__nome',
            values='total_frete',
            title='Participação do Frete por Fornecedor',
            hole=0.55,
        )
        fig_fornecedor.update_traces(
            textinfo='percent+label', textposition='outside',
            textfont=dict(size=11, color='#e2e8f0'),
            marker=dict(line=dict(color='#0d1929', width=2)),
            pull=[0.03] * len(fornecedor_totais),
        )
        grafico_fornecedor = _figure_to_html(fig_fornecedor)
    else:
        grafico_fornecedor = _empty_chart('Participação do Frete por Fornecedor')

    if frete_medio_produto:
        nomes = [d['produto__nome'] for d in frete_medio_produto]
        valores = [float(d['frete_medio']) for d in frete_medio_produto]
        fig_frete_medio = go.Figure(go.Bar(
            y=nomes, x=valores, orientation='h',
            marker=dict(color='#ff6b6b', line=dict(width=0)),
            opacity=0.9,
            text=[f'R$ {v:.4f}' for v in valores],
            textposition='outside',
            textfont=dict(size=11, color='#e2e8f0'),
        ))
        fig_frete_medio.update_layout(
            title='Frete Médio por Produto (R$/L)',
            xaxis_title='', yaxis_title='',
            yaxis=dict(autorange='reversed'),
        )
        grafico_frete_medio = _hbar_to_html(fig_frete_medio, len(nomes))
    else:
        grafico_frete_medio = _empty_chart('Frete Médio por Produto (R$/L)')

    if volume_por_posto:
        nomes_posto = [d['caminhao__local_carregamento__nome'] or '—' for d in volume_por_posto]
        litros_posto = [float(d['total_litros'] or 0) for d in volume_por_posto]
        fig_volume_posto = go.Figure(go.Bar(
            y=nomes_posto, x=litros_posto, orientation='h',
            marker=dict(color='#00d9a6', line=dict(width=0)),
            opacity=0.9,
            text=[f'{v:,.0f} L' for v in litros_posto],
            textposition='outside',
            textfont=dict(size=11, color='#e2e8f0'),
        ))
        fig_volume_posto.update_layout(
            title='Volume por Local de Carregamento',
            xaxis_title='', yaxis_title='',
            yaxis=dict(autorange='reversed'),
        )
        grafico_volume_posto = _hbar_to_html(fig_volume_posto, len(nomes_posto))
    else:
        grafico_volume_posto = _empty_chart('Volume por Local de Carregamento')

    if fornecedor_litros:
        nomes_forn = [d['fornecedor__nome'] for d in fornecedor_litros]
        litros_forn = [float(d['total_litros'] or 0) for d in fornecedor_litros]
        fig_volume_fornecedor = go.Figure(go.Bar(
            y=nomes_forn, x=litros_forn, orientation='h',
            marker=dict(color='#f59e0b', line=dict(width=0)),
            opacity=0.9,
            text=[f'{v:,.0f} L' for v in litros_forn],
            textposition='outside',
            textfont=dict(size=11, color='#e2e8f0'),
        ))
        fig_volume_fornecedor.update_layout(
            title='Volume Carregado por Fornecedor',
            xaxis_title='', yaxis_title='',
            yaxis=dict(autorange='reversed'),
        )
        grafico_volume_fornecedor = _hbar_to_html(fig_volume_fornecedor, len(nomes_forn))
    else:
        grafico_volume_fornecedor = _empty_chart('Volume Carregado por Fornecedor')

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
        'relatorio_abastecimentos': get_relatorio_abastecimentos(params),
        'hoje': date.today(),
    }
