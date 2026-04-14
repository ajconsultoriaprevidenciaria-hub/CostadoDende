PACOTE DE HOSPEDAGEM - COSTA DO DENDE

Arquivos principais para upload:
- passenger_wsgi.py
- manage.py
- deploy_requirements.txt
- config/
- apps/
- templates/
- static/
- staticfiles/
- media/
- db.sqlite3

Configuracao recomendada no servidor:
1. Python app / WSGI apontando para passenger_wsgi.py
2. Variavel DJANGO_SETTINGS_MODULE=config.settings_production
3. Variavel DJANGO_SECRET_KEY com uma chave secreta propria
4. Variavel DJANGO_ALLOWED_HOSTS com o dominio, ex: meusite.com,www.meusite.com
5. Instalar dependencias com: pip install -r deploy_requirements.txt

Se a hospedagem usar cPanel Python App:
1. Envie o conteudo da pasta deploy_upload
2. Configure a aplicacao Python para apontar para passenger_wsgi.py
3. Reinicie a aplicacao

Observacao:
- Este projeto nao e estatico. Nao existe upload apenas de index.html.
- O banco sqlite esta incluido. Se quiser usar outro banco, ajuste config/settings_production.py.