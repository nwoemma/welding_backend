from .base import *
import os
import dj_database_url

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG =  True
SECRET_KEY = 'django-insecure-5s^^j6r5n^x2pu+e!nn+&2jxr^=!4*=*$1p@o5=ikpk#kh6_+u'
ALLOWED_HOSTS = [
    "welding-backend-vm1n.onrender.com",
    "welding-backend.onrender.com",
]

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'welder_app_backend_db',
        'USER': 'welder_user',
        'PASSWORD': 'chznydwDty71uvVFZB4TZqoPCIsjKpQT',
        'HOST': 'dpg-d29a6hadbo4c73b9la9g-a',
        'PORT': '5432',
        # Add this line if your host requires SSL
        # 'OPTIONS': {
        #     'sslmode': 'require',
        # },
    }
}

# else:
#     # Local development default database (SQLite)
#     DATABASES = {
#         'default': {
#             'ENGINE': 'django.db.backends.sqlite3',
#             'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#         }
#     }
# SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
# DEBUG = os.environ.get('DEBUG', 'False') == 'True'
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('DB_NAME'),
#         'USER': os.environ.get('DB_USER'),
#         'PASSWORD': os.environ.get('DB_PASSWORD'),
#         'HOST': os.environ.get('DB_HOST'),
#         'PORT': os.environ.get('DB_PORT'),
#     }
# }

STATIC_ROOT = BASE_DIR/ 'static'




LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "root": {"level": "INFO", "handlers": ["file"]},
    "handlers": {
        "file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename":  os.path.join(BASE_DIR, 'social_log.log'),
            "formatter": "app",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "INFO",
            "propagate": True
        },
    },
    "formatters": {
        "app": {
            "format": (
                u"%(asctime)s [%(levelname)-8s] "
                "(%(module)s.%(funcName)s) %(message)s"
            ),
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
}

