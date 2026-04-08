from django import forms

from .models import Carga


class CargaForm(forms.ModelForm):
    class Meta:
        model = Carga
        fields = [
            'data_carga',
            'cliente',
            'fornecedor',
            'produto',
            'caminhao',
            'motorista',
            'rota',
            'litros',
            'valor_frete_litro',
            'numero_documento',
            'observacoes',
        ]
        widgets = {
            'data_carga': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'cliente': forms.Select(attrs={'class': 'form-select'}),
            'fornecedor': forms.Select(attrs={'class': 'form-select'}),
            'produto': forms.Select(attrs={'class': 'form-select'}),
            'caminhao': forms.Select(attrs={'class': 'form-select'}),
            'motorista': forms.Select(attrs={'class': 'form-select'}),
            'rota': forms.Select(attrs={'class': 'form-select'}),
            'litros': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'id': 'id_litros'}),
            'valor_frete_litro': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.0001', 'id': 'id_valor_frete_litro'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        labels = {
            'valor_frete_litro': 'Valor do frete por litro (R$)',
        }

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data
