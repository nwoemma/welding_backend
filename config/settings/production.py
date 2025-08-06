from .base import *
import os
import dj_database_url
import sys

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
        'NAME': 'welder_app_backend_db_4r6e',
        'USER': 'welder_user',
        'PASSWORD': 'H8q6ped5s40EJLXLMgAanVnv2YOo1gRC',
        'HOST': 'dpg-d29mkc6uk2gs73f6ofeg-a',
        'PORT': '5432',
        'CONN_MAX_AGE': 600,
        # Add this line if your host requires SSL
        # 'OPTIONS': {
        #     'sslmode': 'require',
        # },
    }
}


if 'migrate' in sys.argv or 'runserver' in sys.argv:
    # Temporary direct table creation
    from django.db import connection
    
    with connection.cursor() as cursor:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accounts_user (
                id serial PRIMARY KEY,
                password varchar(128) NOT NULL,
                last_login timestamp with time zone NULL,
                is_superuser boolean NOT NULL,
                username varchar(150) NOT NULL UNIQUE,
                first_name varchar(150) NOT NULL,
                last_name varchar(150) NOT NULL,
                email varchar(254) NOT NULL UNIQUE,
                is_staff boolean NOT NULL,
                is_active boolean NOT NULL,
                date_joined timestamp with time zone NOT NULL,
                phone varchar(15) NULL,
                address text NULL,
                role varchar(20) NULL,
                status varchar(1) NULL
            );
        """)
        print("⚠️ TEMPORARY: Created accounts_user table directly")

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

AUTH_USER_MODEL = 'accounts.User'


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

