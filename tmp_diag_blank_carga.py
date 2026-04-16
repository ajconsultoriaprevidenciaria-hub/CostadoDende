import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django

django.setup()

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sessions.backends.db import SessionStore

User = get_user_model()
user = User.objects.filter(is_superuser=True).first()
if not user:
    raise SystemExit('No superuser found')

session = SessionStore()
session['_auth_user_id'] = str(user.pk)
session['_auth_user_backend'] = 'django.contrib.auth.backends.ModelBackend'
session['_auth_user_hash'] = user.get_session_auth_hash()
session.save()

from playwright.sync_api import sync_playwright

BASE_URL = 'http://127.0.0.1:8000'

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context()
    context.add_cookies([{
        'name': settings.SESSION_COOKIE_NAME,
        'value': session.session_key,
        'domain': '127.0.0.1',
        'path': '/',
        'httpOnly': True,
        'secure': False,
        'sameSite': 'Lax',
    }])
    page = context.new_page()
    page.set_default_timeout(15000)
    logs = []
    errs = []
    page.on('console', lambda msg: logs.append(f'{msg.type}: {msg.text}'))
    page.on('pageerror', lambda err: errs.append(str(err)))

    resp = page.goto(f'{BASE_URL}/admin/fretes/carga/add/', wait_until='domcontentloaded')
    page.wait_for_timeout(1200)

    html = page.content()
    print('resp_status', resp.status if resp else None)
    print('resp_url', resp.url if resp else None)
    print('url', page.url)
    print('title', page.title())
    print('content_len', len(html))
    print('html_preview', repr(html[:180]))
    print('has_adm_shell', 'adm-shell' in html)
    print('has_sidebar', 'adm-sb' in html)
    print('has_content_main', 'content-main' in html)
    print('console_count', len(logs))
    for line in logs[:12]:
        print('console', line)
    print('pageerror_count', len(errs))
    for line in errs[:12]:
        print('pageerror', line)

    page.screenshot(path='tmp_diag_blank_carga.png', full_page=True)
    browser.close()
