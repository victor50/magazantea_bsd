DEBUG = False
ALLOWED_HOSTS=['*']
#TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',#, 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'magazzino',                      # Or path to database file if using sqlite3.
        'USER': 'antea',                      # Not used with sqlite3.
        'PASSWORD': 'antea',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    },
}


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_cache_manager',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'magazzino',
    'spider',
)

if DEBUG:
    INSTALLED_APPS += (
        'debug_toolbar',
    )
