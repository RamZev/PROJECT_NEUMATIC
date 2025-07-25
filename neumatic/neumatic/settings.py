# neumatic\neumatic\settings.py
import locale
from pathlib import Path
from dotenv import load_dotenv
from os import path, getenv

#-- Cargar las variables de entorno del archivo .env
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.maestros',
    'apps.usuarios',
    'apps.ventas',
    'apps.informes',
    'apps.datatools',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'neumatic.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # Carpeta templates a nivel del proyecto
			path.join(BASE_DIR, 'templates')    
        ],
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

WSGI_APPLICATION = 'neumatic.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
		'NAME': path.join(BASE_DIR, 'data', 'db_neumatic.db'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'es-ar'

TIME_ZONE = 'America/Argentina/Buenos_Aires'

USE_I18N = True  # Internacionalización.
USE_L10N = True  # Localización.

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = (path.join(BASE_DIR, 'static'),)
STATIC_ROOT = path.join(BASE_DIR, 'staticfiles')

# Archivos media
MEDIA_URL = '/media/'
MEDIA_ROOT = path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# URL de redireccionamiento de la vista para iniciar sesión.
LOGIN_URL = '/usuarios/sesion/iniciar/'
# URL de redireccionamiento una vez logueado.
LOGIN_REDIRECT_URL = '/'
# URL de redireccionamiento al cerrar sesión.
LOGOUT_REDIRECT_URL = '/usuarios/sesion/iniciar/'

# Para evitar el "secuestro" de la sesión de usuario por JavaScript desde el front.
SESSION_COOKIE_HTTPONLY = True

# La sesión del usuario se cierra al cerrar el navegador.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Modelo Usuario personalizado.
AUTH_USER_MODEL = 'usuarios.User'


#-- Configuración del locale para Argentina/España.
try:
    locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')  # Linux/Mac
except locale.Error:
    locale.setlocale(locale.LC_ALL, 'spanish')      # Windows como fallback