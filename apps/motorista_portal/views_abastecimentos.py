from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.shortcuts import render
from .models import AbastecimentoViagem

@login_required
def lista_abastecimentos(request):
    # Agrupa por posto
    qs = AbastecimentoViagem.objects.values('posto').annotate(
        total_litros=Sum('litros'),
        total_abastecimentos=Count('id'),
        total_valor=Sum('despesa__valor'),
    ).order_by('posto')
    return render(request, 'motorista_portal/abastecimentos_list.html', {
        'postos': qs,
    })
