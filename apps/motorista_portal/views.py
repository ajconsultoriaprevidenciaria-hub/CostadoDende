from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from apps.fretes.models import Carga, Motorista

from .forms import ChecklistForm, DespesaForm, ItemChecklistForm
from .models import (
    AbastecimentoViagem,
    ChecklistViagem,
    DespesaViagem,
    ItemChecklist,
)


# ── Auth ──────────────────────────────────────────────────────

def login_motorista(request):
    if request.method == 'POST':
        cpf = request.POST.get('cpf', '').strip()
        senha = request.POST.get('senha', '')
        user = authenticate(request, cpf=cpf, password=senha)
        if user is not None:
            login(request, user)
            return redirect('motorista_portal:painel')
        messages.error(request, 'CPF ou senha inválidos.')
    return render(request, 'motorista_portal/login.html')


def logout_motorista(request):
    logout(request)
    return redirect('motorista_portal:login')


# ── Helpers ───────────────────────────────────────────────────

def _get_motorista(user):
    return get_object_or_404(Motorista, user=user)


# ── Painel ────────────────────────────────────────────────────

@login_required(login_url='motorista_portal:login')
def painel(request):
    motorista = _get_motorista(request.user)
    cargas = Carga.objects.filter(motorista=motorista, ativo=True).order_by('-data_carga')[:10]
    return render(request, 'motorista_portal/painel.html', {
        'motorista': motorista,
        'cargas': cargas,
    })


# ── Carga detail ──────────────────────────────────────────────

@login_required(login_url='motorista_portal:login')
def carga_detalhe(request, pk):
    motorista = _get_motorista(request.user)
    carga = get_object_or_404(Carga, pk=pk, motorista=motorista)
    checklists = carga.checklists.all()
    despesas = carga.despesas.all()
    tem_checklist = checklists.filter(concluido=True).exists()
    return render(request, 'motorista_portal/carga_detalhe.html', {
        'motorista': motorista,
        'carga': carga,
        'checklists': checklists,
        'despesas': despesas,
        'tem_checklist': tem_checklist,
    })


# ── Checklist ─────────────────────────────────────────────────

CATEGORIAS_OBRIGATORIAS = [
    'pneus', 'retrovisores', 'parabrisa', 'tanque',
    'farois', 'freios', 'documentos',
]


@login_required(login_url='motorista_portal:login')
def checklist_criar(request, carga_pk):
    motorista = _get_motorista(request.user)
    carga = get_object_or_404(Carga, pk=carga_pk, motorista=motorista)

    if request.method == 'POST':
        form = ChecklistForm(request.POST)
        if form.is_valid():
            checklist = ChecklistViagem.objects.create(
                carga=carga,
                motorista=motorista,
                observacoes=form.cleaned_data['observacoes'],
            )
            all_ok = True
            for cat in CATEGORIAS_OBRIGATORIAS:
                foto = request.FILES.get(f'foto_{cat}')
                status = request.POST.get(f'status_{cat}', 'ok')
                obs = request.POST.get(f'obs_{cat}', '')
                if foto:
                    ItemChecklist.objects.create(
                        checklist=checklist,
                        categoria=cat,
                        status=status,
                        foto=foto,
                        observacao=obs,
                    )
                else:
                    all_ok = False

            if all_ok:
                checklist.concluido = True
                checklist.save()
                messages.success(request, 'Checklist concluído com sucesso!')
                return redirect('motorista_portal:carga-detalhe', pk=carga.pk)
            else:
                checklist.delete()
                messages.error(request, 'Envie a foto de todas as categorias.')
    else:
        form = ChecklistForm()

    categorias = [
        {'key': c, 'label': dict(ItemChecklist.CATEGORIA_CHOICES).get(c, c)}
        for c in CATEGORIAS_OBRIGATORIAS
    ]
    return render(request, 'motorista_portal/checklist_form.html', {
        'carga': carga,
        'form': form,
        'categorias': categorias,
    })


@login_required(login_url='motorista_portal:login')
def checklist_detalhe(request, pk):
    motorista = _get_motorista(request.user)
    checklist = get_object_or_404(
        ChecklistViagem, pk=pk, motorista=motorista,
    )
    return render(request, 'motorista_portal/checklist_detalhe.html', {
        'checklist': checklist,
    })


# ── Despesas ──────────────────────────────────────────────────

@login_required(login_url='motorista_portal:login')
def despesa_criar(request, carga_pk):
    motorista = _get_motorista(request.user)
    carga = get_object_or_404(Carga, pk=carga_pk, motorista=motorista)

    # Exige checklist concluído
    if not carga.checklists.filter(concluido=True).exists():
        messages.warning(request, 'Conclua o checklist antes de registrar despesas.')
        return redirect('motorista_portal:carga-detalhe', pk=carga.pk)

    if request.method == 'POST':
        form = DespesaForm(request.POST, request.FILES)
        if form.is_valid():
            d = form.cleaned_data
            despesa = DespesaViagem.objects.create(
                carga=carga,
                motorista=motorista,
                tipo=d['tipo'],
                descricao=d['descricao'],
                valor=d['valor'],
                data=d['data'],
                comprovante=d.get('comprovante') or '',
            )
            if d['tipo'] == 'abastecimento':
                AbastecimentoViagem.objects.create(
                    despesa=despesa,
                    posto=d['posto'],
                    litros=d['litros'],
                    preco_litro=d['preco_litro'],
                    foto_cupom=d['foto_cupom'],
                )
            messages.success(request, 'Despesa registrada!')
            return redirect('motorista_portal:carga-detalhe', pk=carga.pk)
    else:
        form = DespesaForm()

    return render(request, 'motorista_portal/despesa_form.html', {
        'carga': carga,
        'form': form,
    })


@login_required(login_url='motorista_portal:login')
def despesa_detalhe(request, pk):
    motorista = _get_motorista(request.user)
    despesa = get_object_or_404(DespesaViagem, pk=pk, motorista=motorista)
    return render(request, 'motorista_portal/despesa_detalhe.html', {
        'despesa': despesa,
    })

