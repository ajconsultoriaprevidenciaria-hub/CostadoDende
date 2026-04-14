from django import forms


class CPFLoginForm(forms.Form):
    cpf = forms.CharField(
        max_length=14,
        widget=forms.TextInput(attrs={
            'placeholder': '000.000.000-00',
            'inputmode': 'numeric',
            'autocomplete': 'off',
        }),
        label='CPF',
    )
    senha = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Sua senha',
        }),
        label='Senha',
    )


class ChecklistForm(forms.Form):
    observacoes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Observações gerais...'}),
    )


class ItemChecklistForm(forms.Form):
    CATEGORIA_CHOICES = [
        ('pneus', 'Pneus'),
        ('retrovisores', 'Retrovisores'),
        ('parabrisa', 'Para-brisa'),
        ('tanque', 'Tanque'),
        ('farois', 'Faróis'),
        ('freios', 'Freios'),
        ('documentos', 'Documentos'),
        ('outros', 'Outros'),
    ]

    STATUS_CHOICES = [
        ('ok', 'OK'),
        ('atencao', 'Atenção'),
        ('critico', 'Crítico'),
    ]

    categoria = forms.CharField(widget=forms.HiddenInput())
    status = forms.ChoiceField(choices=STATUS_CHOICES, initial='ok')
    foto = forms.ImageField()
    observacao = forms.CharField(required=False, max_length=255)


class DespesaForm(forms.Form):
    TIPO_CHOICES = [
        ('pedagio', 'Pedágio'),
        ('alimentacao', 'Alimentação'),
        ('manutencao', 'Manutenção'),
        ('hospedagem', 'Hospedagem'),
        ('abastecimento', 'Abastecimento'),
        ('outros', 'Outros'),
    ]

    tipo = forms.ChoiceField(choices=TIPO_CHOICES)
    descricao = forms.CharField(required=False, max_length=255)
    valor = forms.DecimalField(max_digits=10, decimal_places=2)
    data = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    comprovante = forms.ImageField(required=False)

    # Campos de abastecimento (opcionais, mostrados via JS quando tipo=abastecimento)
    posto = forms.CharField(required=False, max_length=200)
    litros = forms.DecimalField(required=False, max_digits=10, decimal_places=2)
    preco_litro = forms.DecimalField(required=False, max_digits=8, decimal_places=4)
    foto_cupom = forms.ImageField(required=False)

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('tipo') == 'abastecimento':
            for campo in ('posto', 'litros', 'preco_litro', 'foto_cupom'):
                if not cleaned.get(campo):
                    self.add_error(campo, 'Obrigatório para abastecimento.')
        return cleaned
