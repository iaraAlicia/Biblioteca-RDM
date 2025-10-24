"""
Django settings for biblioteca_virtual project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
import dj_database_url # Certifique-se que está importado

load_dotenv() # Carrega .env localmente

BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production

# --- CORREÇÃO SECRET_KEY ---
# Pega a chave da variável de ambiente 'SECRET_KEY'
SECRET_KEY = os.environ.get('SECRET_KEY')
# Medida de segurança: Se a SECRET_KEY não estiver definida em produção, o app não inicia.
if not SECRET_KEY and os.environ.get('RENDER'): # RENDER define a variável 'RENDER' automaticamente
    raise ValueError("No SECRET_KEY set for production")

# --- CORREÇÃO DEBUG ---
# Lê a variável DEBUG do ambiente, padrão 'False'
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# --- ALLOWED_HOSTS (Parece correto, mas garantindo) ---
ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
ALLOWED_HOSTS.append('.onrender.com') # Permite qualquer subdomínio do Render
# Adiciona hosts locais apenas se DEBUG for True
if DEBUG:
    ALLOWED_HOSTS.append('127.0.0.1')
    ALLOWED_HOSTS.append('localhost')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'acervo'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Correto
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'biblioteca_virtual.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Correto
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'biblioteca_virtual.wsgi.application' # Correto


# --- CORREÇÃO DATABASES ---
# Usa dj_database_url para ler a variável DATABASE_URL do ambiente
DATABASES = {
    'default': dj_database_url.config(
        # Define um valor padrão caso DATABASE_URL não exista (útil para testes locais sem .env)
        default=os.environ.get('DATABASE_URL', f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
        conn_max_age=600 # Tempo de vida da conexão (bom para produção)
    )
}


# Password validation
# ... (AUTH_PASSWORD_VALIDATORS - sem alterações) ...

# Internationalization
LANGUAGE_CODE = 'pt-br' # Mudado para Português-Brasil
TIME_ZONE = 'America/Recife' # Correto
USE_I18N = True
USE_TZ = True # Correto

# Static files (CSS, JavaScript, Images)
STATIC_URL = 'static/' # Correto
STATICFILES_DIRS = [BASE_DIR / "static"] # Correto
STATIC_ROOT = BASE_DIR / "staticfiles" # Correto
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage' # Correto

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Login URLs (Corretos)
LOGIN_REDIRECT_URL = 'dashboard'
LOGIN_URL = 'login'