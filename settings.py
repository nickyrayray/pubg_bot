INSTALLED_APPS = ('data_access',)

SECRET_KEY = '12345'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pubg_stats',
        'USER': 'pubgadmin',
        'PASSWORD': 'pubgpass',
        'HOST': 'mysql',
        'PORT': 3306
    }
}