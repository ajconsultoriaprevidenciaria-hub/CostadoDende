from django.urls import path

from .views import HomeView, estoque_view, root_redirect

app_name = 'core'

urlpatterns = [
    path('', root_redirect, name='root'),
    path('inicio/', HomeView.as_view(), name='home'),
    path('estoque/', estoque_view, name='estoque'),
]
