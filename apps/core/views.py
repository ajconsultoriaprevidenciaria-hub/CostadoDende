from django.shortcuts import redirect
from django.views.generic import TemplateView


class HomeView(TemplateView):
	template_name = 'core/home.html'


def root_redirect(request):
	if request.user.is_authenticated:
		return redirect('dashboard:index')
	return redirect('login')
