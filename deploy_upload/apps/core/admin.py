from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.urls import reverse


PERFIL_CHOICES = [
    ('admin', 'Administrador'),
    ('motorista', 'Motorista'),
    ('comum', 'Usuário Comum'),
]


class CustomUserCreationForm(forms.ModelForm):
    cpf = forms.CharField(
        max_length=14,
        label='CPF',
        widget=forms.TextInput(attrs={'style': 'width:100%', 'placeholder': '000.000.000-00'}),
    )
    nome_completo = forms.CharField(
        max_length=150,
        label='Nome completo',
        widget=forms.TextInput(attrs={'style': 'width:100%'}),
    )
    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={'style': 'width:100%'}),
    )
    telefone = forms.CharField(
        max_length=20,
        label='Contato telefônico',
        required=False,
        widget=forms.TextInput(attrs={'style': 'width:100%', 'placeholder': '(00) 00000-0000'}),
    )
    perfil = forms.ChoiceField(
        choices=PERFIL_CHOICES,
        label='Tipo de usuário',
        widget=forms.RadioSelect,
    )
    senha = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'style': 'width:100%'}),
    )
    confirmar_senha = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={'style': 'width:100%'}),
    )

    class Meta:
        model = User
        fields = ('cpf', 'nome_completo', 'email', 'telefone', 'perfil', 'senha', 'confirmar_senha')

    def clean_cpf(self):
        import re
        cpf = re.sub(r'\D', '', self.cleaned_data.get('cpf', ''))
        if len(cpf) != 11:
            raise forms.ValidationError('CPF deve conter 11 dígitos.')
        if User.objects.filter(username=cpf).exists():
            raise forms.ValidationError('Já existe um usuário cadastrado com este CPF.')
        return cpf

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('senha') and cleaned.get('confirmar_senha'):
            if cleaned['senha'] != cleaned['confirmar_senha']:
                raise forms.ValidationError('As senhas não conferem.')
        return cleaned

    def save(self, commit=True):
        nome = self.cleaned_data['nome_completo'].strip()
        email = self.cleaned_data['email'].strip().lower()
        perfil = self.cleaned_data['perfil']
        username = self.cleaned_data['cpf']  # username = CPF (só dígitos)

        partes = nome.split(' ', 1)
        first_name = partes[0]
        last_name = partes[1] if len(partes) > 1 else ''

        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(self.cleaned_data['senha'])

        if perfil == 'admin':
            user.is_staff = True
            user.is_superuser = True
        elif perfil == 'motorista':
            user.is_staff = False
            user.is_superuser = False
        else:
            user.is_staff = True
            user.is_superuser = False

        # save_m2m é chamado pelo admin após save_related
        self.save_m2m = lambda: None

        if commit:
            user.save()

            # Se motorista, tenta vincular ao cadastro de Motorista pelo telefone/nome
            if perfil == 'motorista':
                telefone = self.cleaned_data.get('telefone', '')
                from apps.fretes.models import Motorista
                motorista = Motorista.objects.filter(user__isnull=True, nome__iexact=nome).first()
                if motorista:
                    motorista.user = user
                    if telefone:
                        motorista.telefone = telefone
                    motorista.save()

        return user


class CustomUserChangeForm(forms.ModelForm):
    password = forms.CharField(
        label='Senha',
        required=False,
        widget=forms.HiddenInput,
    )

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'username' in self.fields:
            self.fields['username'].help_text = ''


class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    add_form_template = 'admin/auth/user/custom_add_form.html'
    add_fieldsets = None  # Não usar fieldsets padrão no add
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'acoes')

    class Media:
        css = {'all': ()}

    class Meta:
        pass

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['adminform_css'] = (
            '<style>'
            '.form-row { padding: 6px 12px !important; }'
            'fieldset { margin-bottom: 8px !important; padding: 8px 12px !important; }'
            '.help, .help-text { display: none !important; }'
            '.aligned label { padding: 4px 0 !important; }'
            '</style>'
        )
        return super().changeform_view(request, object_id, form_url, extra_context)

    @admin.display(description='Ações')
    def acoes(self, obj):
        edit_url = reverse('admin:auth_user_change', args=[obj.pk])
        delete_url = reverse('admin:auth_user_delete', args=[obj.pk])
        return format_html(
            '<a href="{}" title="Editar" style="margin-right:10px;color:#4fc3f7;">'
            '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" '
            'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>'
            '<path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg></a>'
            '<a href="{}" title="Excluir" style="color:#ef5350;">'
            '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" '
            'fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
            '<polyline points="3 6 5 6 21 6"/>'
            '<path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>'
            '<line x1="10" y1="11" x2="10" y2="17"/>'
            '<line x1="14" y1="11" x2="14" y2="17"/></svg></a>',
            edit_url, delete_url
        )

    fieldsets = (
        ('Informações Pessoais', {
            'fields': ('first_name', 'last_name', 'email'),
        }),
        ('Acesso', {
            'fields': ('username', 'password', 'is_active'),
        }),
        ('Permissões', {
            'fields': ('is_staff', 'is_superuser'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return []
        return self.fieldsets

    def get_fields(self, request, obj=None):
        if not obj:
            return ['cpf', 'nome_completo', 'email', 'telefone', 'perfil', 'senha', 'confirmar_senha']
        return super().get_fields(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
