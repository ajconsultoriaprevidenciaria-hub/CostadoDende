import os

from .settings import *  # noqa: F401,F403

DEBUG = True  # Temporário para debug

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
]
_csrf_extra = os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '')
CSRF_TRUSTED_ORIGINS += [
    o.strip() for o in _csrf_extra.split(',') if o.strip()
]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_AGE = 60 * 60 * 24 * 7  # 7 dias

MEDIA_SERVE_BY_DJANGO = True

# Banco de dados — produção sempre usa PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}
