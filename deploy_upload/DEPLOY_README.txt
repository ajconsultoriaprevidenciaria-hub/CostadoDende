DEPLOY - COSTA DO DENDE - postoscostadodende.com.br
====================================================

PASSO A PASSO PARA HOSTINGER:

1. Acesse hPanel > Avancado > Aplicativo Python (Setup Python App)
2. Crie uma aplicacao Python:
   - Python version: 3.12 (ou a mais recente disponivel)
   - App root: public_html (ou a pasta do dominio)
   - App URL: postoscostadodende.com.br
   - Startup file: passenger_wsgi.py
3. Faca upload de TODOS os arquivos desta pasta para o App root
   (pode enviar o ZIP pelo Gerenciador de Arquivos e extrair la)
4. No terminal SSH da Hostinger, ative o virtualenv e instale:
   source /home/SEUUSUARIO/virtualenv/public_html/3.12/bin/activate
   pip install -r deploy_requirements.txt
5. Configure variaveis de ambiente no painel do Python App:
   DJANGO_SETTINGS_MODULE = config.settings_production
   DJANGO_SECRET_KEY = (gere com: python -c "import secrets; print(secrets.token_urlsafe(50))")
6. No terminal SSH, rode as migracoes:
   python manage.py migrate --settings=config.settings_production
   python manage.py collectstatic --noinput --settings=config.settings_production
7. Reinicie a aplicacao Python no hPanel
8. Ative o SSL gratuito (Let's Encrypt) em hPanel > SSL

ESTRUTURA:
- passenger_wsgi.py   -> ponto de entrada WSGI
- manage.py           -> comandos Django
- config/             -> configuracoes
- apps/               -> aplicacoes (fretes, dashboard, motorista_portal, core)
- templates/          -> templates HTML
- static/             -> arquivos estaticos (fonte)
- staticfiles/        -> arquivos estaticos (compilados)
- media/              -> uploads (fotos, documentos)
- db.sqlite3          -> banco de dados

DOMINIO: postoscostadodende.com.br