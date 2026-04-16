from datetime import datetime
from io import BytesIO

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.http import FileResponse
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from apps.fretes.models import Cliente

from .models import AbastecimentoViagem


@ensure_csrf_cookie
@login_required
def lista_abastecimentos(request):
    posto = request.GET.get('posto', '').strip()
    data_inicial = request.GET.get('data_inicial', '').strip()
    data_final = request.GET.get('data_final', '').strip()
    mes = request.GET.get('mes', '').strip()

    qs = AbastecimentoViagem.objects.select_related('despesa')

    if posto:
        qs = qs.filter(posto__icontains=posto)

    if data_inicial:
        qs = qs.filter(despesa__data__gte=data_inicial)

    if data_final:
        qs = qs.filter(despesa__data__lte=data_final)

    if mes:
        try:
            data_mes = datetime.strptime(mes, '%Y-%m')
            qs = qs.filter(
                despesa__data__year=data_mes.year,
                despesa__data__month=data_mes.month,
            )
        except ValueError:
            mes = ''

    postos = qs.values('posto').annotate(
        total_litros=Sum('litros'),
        total_abastecimentos=Count('id'),
        total_valor=Sum('despesa__valor'),
    ).order_by('posto')

    sugestoes_postos = Cliente.objects.filter(ativo=True).order_by('nome').values_list('nome', flat=True)
    ano_atual = datetime.now().year

    selected_month = ''
    selected_year = ano_atual
    if mes:
        try:
            mes_data = datetime.strptime(mes, '%Y-%m')
            selected_month = f'{mes_data.month:02d}'
            selected_year = mes_data.year
        except ValueError:
            pass

    is_admin = request.user.is_staff
    template = 'admin/abastecimentos_list.html' if is_admin else 'motorista_portal/abastecimentos_list.html'

    context = {
        'postos': postos,
        'sugestoes_postos': sugestoes_postos,
        'anos_disponiveis': range(ano_atual - 10, ano_atual + 11),
        'selected_month': selected_month,
        'selected_year': selected_year,
        'filtros': {
            'posto': posto,
            'data_inicial': data_inicial,
            'data_final': data_final,
            'mes': mes,
        },
    }

    if is_admin:
        context.update(admin.site.each_context(request))
        context['title'] = 'Abastecimentos por Posto'

    return render(request, template, context)


@login_required
def exportar_abastecimentos_pdf(request):
    posto = request.GET.get('posto', '').strip()
    data_inicial = request.GET.get('data_inicial', '').strip()
    data_final = request.GET.get('data_final', '').strip()
    mes = request.GET.get('mes', '').strip()

    qs = AbastecimentoViagem.objects.select_related(
        'despesa', 'despesa__carga', 'despesa__carga__caminhao',
        'despesa__carga__rota', 'despesa__motorista',
    )

    if posto:
        qs = qs.filter(posto__icontains=posto)
    if data_inicial:
        qs = qs.filter(despesa__data__gte=data_inicial)
    if data_final:
        qs = qs.filter(despesa__data__lte=data_final)
    if mes:
        try:
            data_mes = datetime.strptime(mes, '%Y-%m')
            qs = qs.filter(
                despesa__data__year=data_mes.year,
                despesa__data__month=data_mes.month,
            )
        except ValueError:
            pass

    qs = qs.order_by('-despesa__data')

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=landscape(A4),
        leftMargin=15 * mm, rightMargin=15 * mm,
        topMargin=15 * mm, bottomMargin=15 * mm,
    )
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph('Relatório de Abastecimentos — Costa do Dendê', styles['Title']))
    story.append(Spacer(1, 4 * mm))

    filtros_txt = []
    if posto:
        filtros_txt.append(f'Posto: {posto}')
    if data_inicial:
        filtros_txt.append(f'De: {data_inicial}')
    if data_final:
        filtros_txt.append(f'Até: {data_final}')
    if mes:
        filtros_txt.append(f'Mês: {mes}')
    if filtros_txt:
        story.append(Paragraph('Filtros: ' + ' | '.join(filtros_txt), styles['Normal']))
        story.append(Spacer(1, 3 * mm))

    data = [['Data', 'Posto', 'Litros', 'R$/Litro', 'Valor (R$)', 'Caminhão', 'Motorista', 'Viagem (Rota)']]
    for ab in qs:
        desp = ab.despesa
        carga = desp.carga
        data.append([
            desp.data.strftime('%d/%m/%Y'),
            ab.posto[:30],
            f'{ab.litros:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
            f'{ab.preco_litro:,.4f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
            f'{desp.valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
            carga.caminhao.placa if carga else '-',
            str(desp.motorista) if desp.motorista else '-',
            str(carga.rota) if carga and carga.rota else '-',
        ])

    col_widths = [62, 110, 60, 60, 70, 62, 120, 180]
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d1929')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#00d9a6')),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 8),
        ('FONTSIZE', (0, 1), (-1, -1), 7),
        ('ALIGN', (2, 0), (4, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#333333')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f5f5f5')]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(t)

    doc.build(story)
    buffer.seek(0)
    return FileResponse(buffer, as_attachment=True, filename='relatorio_abastecimentos.pdf')
