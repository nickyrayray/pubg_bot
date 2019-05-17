import os

INSTALLED_APPS = ('game_data',)

SECRET_KEY = '12345'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pubg_stats',
        'USER': 'pubgadmin',
        'PASSWORD': os.environ.get('PUBG_DB_PASS'),
        'HOST': os.environ.get('PUBG_DB_HOST', 'localhost'),
        'PORT': 5432
    }
}