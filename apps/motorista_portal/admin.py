from django.contrib import admin
from django.utils.html import format_html

from .models import (
    AbastecimentoViagem,
    ChecklistViagem,
    DespesaViagem,
    ItemChecklist,
)


class ItemChecklistInline(admin.StackedInline):
    model = ItemChecklist
    extra = 0
    readonly_fields = ('foto_preview',)

    def foto_preview(self, obj):
        if obj.foto:
            return format_html('<img src="{}" style="max-height:60px; border-radius:4px;">', obj.foto.url)
        return '-'
    foto_preview.short_description = 'Foto'


@admin.register(ChecklistViagem)
class ChecklistViagemAdmin(admin.ModelAdmin):
    list_display = ('carga', 'motorista', 'data_hora', 'concluido')
    list_filter = ('concluido', 'data_hora')
    search_fields = ('carga__cliente__nome', 'motorista__nome')
    inlines = [ItemChecklistInline]
    readonly_fields = ('data_hora',)


class AbastecimentoInline(admin.StackedInline):
    model = AbastecimentoViagem
    extra = 0
    readonly_fields = ('cupom_preview',)

    def cupom_preview(self, obj):
        if obj.foto_cupom:
            return format_html('<img src="{}" style="max-height:80px; border-radius:4px;">', obj.foto_cupom.url)
        return '-'
    cupom_preview.short_description = 'Cupom Fiscal'


@admin.register(DespesaViagem)
class DespesaViagemAdmin(admin.ModelAdmin):
    list_display = ('carga', 'motorista', 'tipo', 'valor', 'data')
    list_filter = ('tipo', 'data')
    search_fields = ('carga__cliente__nome', 'motorista__nome', 'descricao')
    inlines = [AbastecimentoInline]

