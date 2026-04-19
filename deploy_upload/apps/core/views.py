from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'core/home.html'


class LandingPageView(TemplateView):
    template_name = 'core/landing.html'


def root_redirect(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
    return LandingPageView.as_view()(request)


@login_required
def estoque_view(request):
    return render(request, 'core/estoque.html')
