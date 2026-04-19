import os
from pathlib import Path

# Carregar variáveis de ambiente do arquivo .env
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).resolve().parent.parent / '.env'
    load_dotenv(env_path)
except ImportError:
    pass

from .settings import *  # noqa: F401,F403

DEBUG = False  # Produção - SSL configurado

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', SECRET_KEY)

allowed_hosts_env = os.getenv('DJANGO_ALLOWED_HOSTS', '')
ALLOWED_HOSTS = [h.strip()
                 for h in allowed_hosts_env.split(',') if h.strip()] or [
                     'postoscostadodende.com.br',
                     'www.postoscostadodende.com.br',
                     'localhost',
                     '127.0.0.1',
                 ]

if 'whitenoise.middleware.WhiteNoiseMiddleware' not in MIDDLEWARE:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

CSRF_TRUSTED_ORIGINS = [
    'https://postoscostadodende.com.br',
    'https://www.postoscostadodende.com.br',
    'http://postoscostadodende.com.br',
    'http://www.postoscostadodende.com.br',
    'http://72.61.27.65',
]
_csrf_extra = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS += [
    o.strip() for o in _csrf_extra.split(',') if o.strip()
]

# Cookies seguros - SSL CONFIGURADO ✅
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7 dias

MEDIA_SERVE_BY_DJANGO = True

# Banco de dados — produção usa PostgreSQL (padrão VPS) ou MySQL
db_engine = os.getenv('DB_ENGINE', 'django.db.backends.postgresql')
default_port = '5432' if 'postgres' in db_engine else '3306'

DATABASES = {
    'default': {
        'ENGINE': db_engine,
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', default_port),
    }
}
