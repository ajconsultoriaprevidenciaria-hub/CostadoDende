from django.urls import path

from .views import DashboardView, export_dashboard_pdf

app_name = 'dashboard'

urlpatterns = [
    path('', DashboardView.as_view(), name='index'),
    path('relatorio.pdf', export_dashboard_pdf, name='export-pdf'),
]
