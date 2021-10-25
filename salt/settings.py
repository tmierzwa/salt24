"""
Django settings for salt project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'xnom9!9^5d4poy&lt!%#-r+fr9-wvyutgbkw!#@q7e%rud$wax'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['salt24.pl', 'www.salt24.pl', '52.58.95.140']

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'debug.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_crontab',
    'camo', 'pdt', 'sms', 'ato', 'panel', 'fin', 'fbo', 'res',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'mobileesp.middleware.MobileDetectionMiddleware',
)

ROOT_URLCONF = 'salt.urls'

WSGI_APPLICATION = 'salt.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    #'default': {
    #    'ENGINE': 'django.db.backends.sqlite3',
    #    'NAME': os.path.join(BASE_DIR, 'db.salt'),
    #}
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'salt',
        'USER': 'salt',
        'PASSWORD': 'C2gtn1!SQL',
        'HOST': 'localhost',
        'PORT': '',
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'pl-pl'
TIME_ZONE = 'Europe/Warsaw'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
ADMIN_MEDIA_PREFIX ='/static/admin/'

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, "salt/static"),
)

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': ['salt/system/salt/templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

LOGIN_REDIRECT_URL = 'dispatcher'
LOGIN_URL = '/login/'
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

DATE_FORMAT = "%Y.%m.%d"
TIME_INPUT_FORMATS = [
    '%H:%M:%S',     # '14:30:59'
    '%H:%M:%S.%f',  # '14:30:59.000200'
    '%H:%M',        # '14:30'
    '%H.%M',        # '14.30'
    '%H%M',         # '1430'
]

# parametryzacja SMS
SMS_TOKEN = '026VEzVzaLHjABm60JYTXQQWRB11ckKwGa7AFQmZ'

# parametryzacja email
EMAIL_FROM = 'salt24@salt.aero'
EMAIL_SUBJECT = 'Wiadomość od SALT24.pl'
EMAIL_HOST = 'poczta21634.kei.pl'
EMAIL_PORT = '465'
EMAIL_HOST_USER = 'salt24@salt.aero'
EMAIL_HOST_PASSWORD = '6l6QDGJt85'
EMAIL_USE_TLS = False
EMAIL_USE_SSL = True
EMAIL_ATO = ['ato@salt.aero']
EMAIL_INFO = ['info@salt.aero']
EMAIL_NCR = ['a.sikorska@salt.aero', 'a.peksa@salt.aero']

# harmonogramy automatyczne

CRONJOBS = [
    ('0  5 * * 1-5', 'res.views.PortSend'),
    ('0 13 * * 5  ', 'res.views.PortSendWeekend'),
	('0  8 * * *'  , 'sms.views.NCRWarnings'),
]