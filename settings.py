INSTALLED_APPS = ('game_data',)

SECRET_KEY = '12345'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'pubg_stats',
        'USER': 'pubgadmin',
        'PASSWORD': 'pubgpass',
        'HOST': 'postgresql',
        'PORT': 5432
    }
}