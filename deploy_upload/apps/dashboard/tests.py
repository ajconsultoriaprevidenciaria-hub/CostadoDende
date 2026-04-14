from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class DashboardViewTest(TestCase):
	def setUp(self):
		self.user = get_user_model().objects.create_user(username='gestor', password='Senha@123')

	def test_dashboard_exige_login(self):
		response = self.client.get(reverse('dashboard:index'))
		self.assertEqual(response.status_code, 302)

	def test_dashboard_autenticado_responde_ok(self):
		self.client.login(username='gestor', password='Senha@123')
		response = self.client.get(reverse('dashboard:index'))
		self.assertEqual(response.status_code, 200)

	def test_exportacao_pdf_responde_ok(self):
		self.client.login(username='gestor', password='Senha@123')
		response = self.client.get(reverse('dashboard:export-pdf'))
		self.assertEqual(response.status_code, 200)
