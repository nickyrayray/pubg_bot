import dj_database_url
import os

INSTALLED_APPS = ('game_data',)

SECRET_KEY = '12345'

databse_url = os.environ.get('DATABASE_URL', None)

if databse_url:
    DATABASES = {
        'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
    }
else:
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