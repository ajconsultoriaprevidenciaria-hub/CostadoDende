from datetime import datetime

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie

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
