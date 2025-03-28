import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('SECRET_KEY')

DEBUG = os.getenv('DEBUG', False)

ALLOWED_HOSTS = ['*']



INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Библиотеки
    'django_extensions',
    
    # Приложения
    'web.apps.telegram_users',
    'web.apps.search',
    'web.apps.bots',
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

ROOT_URLCONF = 'web.core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'web.core.wsgi.application'



DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASS'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', 5432),
    }
}

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

LANGUAGE_CODE = 'ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True

MEDIA_URL = '/media/'
STATIC_URL = 'static/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
REDIS_URL = f'redis://{REDIS_HOST}:{REDIS_PORT}'

CELERY_BROKER_URL = f'{REDIS_URL}/0'
CELERY_RESULT_BACKEND = f'{REDIS_URL}/1'
CELERY_BROKER_TRANSPORT_OPTIONS = {'visibility_timeout': 3600}
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'


# Настройки бота
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME')
BOT_LINK = f'https://t.me/{BOT_USERNAME}'
MAX_MESSAGE_PER_SECOND = int(os.getenv('MAX_MESSAGE_PER_SECOND', 1))
CHATS_PER_PAGE = int(os.getenv('CHATS_PER_PAGE', 5))
KEYWORDS_PER_PAGE = int(os.getenv('KEYWORDS_PER_PAGE', 5))
PROJECTS_PER_PAGE = int(os.getenv('PROJECTS_PER_PAGE', 5))

USER_BOTS_SESSIONS_DIR = 'userbots/sessions/'
USER_BOTS_SESSIONS_DIR_1 = f'{USER_BOTS_SESSIONS_DIR}1/'
USER_BOTS_SESSIONS_ROOT_1 = os.path.join(MEDIA_ROOT, USER_BOTS_SESSIONS_DIR_1)
USER_BOTS_SESSIONS_DIR_2 = f'{USER_BOTS_SESSIONS_DIR}2/'
USER_BOTS_SESSIONS_ROOT_2 = os.path.join(MEDIA_ROOT, USER_BOTS_SESSIONS_DIR_2)

KEYWORDS_MATCHES_BUFFER_GROUP_ID = os.getenv('KEYWORDS_MATCHES_BUFFER_GROUP_ID')

SEARCH_THRESHOLD = os.getenv('SEARCH_THRESHOLD', 90) # % совпадения слова при поиске

TELEGRAM_API_URL = 'https://api.telegram.org'
