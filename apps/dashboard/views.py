from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse
from django.views.generic import TemplateView
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .services import build_dashboard_context, get_filtered_cargas


class DashboardView(LoginRequiredMixin, TemplateView):
	template_name = 'dashboard/index.html'

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context.update(build_dashboard_context(self.request.GET))
		return context


@login_required
def export_dashboard_pdf(request):
	queryset, _ = get_filtered_cargas(request.GET)
	buffer = BytesIO()
	doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=24, rightMargin=24, topMargin=24, bottomMargin=24)
	styles = getSampleStyleSheet()
	story = [
		Paragraph('Costa do Dendê - Relatório de Fretes', styles['Title']),
		Spacer(1, 12),
		Paragraph('Resumo operacional por cliente, produto e fornecedor.', styles['Normal']),
		Spacer(1, 16),
	]

	data = [['Data', 'Cliente', 'Produto', 'Fornecedor', 'Rota', 'Litros', 'R$/L', 'Frete total']]
	for carga in queryset.order_by('-data_carga')[:200]:
		data.append([
			carga.data_carga.strftime('%d/%m/%Y'),
			str(carga.cliente),
			str(carga.produto),
			str(carga.fornecedor),
			str(carga.rota),
			f'{carga.litros:.2f}',
			f'{(carga.valor_frete_litro or 0):.4f}',
			f'{(carga.valor_total_frete or 0):.2f}',
		])

	table = Table(data, repeatRows=1)
	table.setStyle(TableStyle([
		('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f766e')),
		('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
		('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
		('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
		('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor('#eef6f5')]),
		('FONTSIZE', (0, 0), (-1, -1), 9),
		('ALIGN', (5, 1), (-1, -1), 'RIGHT'),
	]))
	story.append(table)

	doc.build(story)
	buffer.seek(0)
	return FileResponse(buffer, as_attachment=True, filename='relatorio_fretes.pdf')
