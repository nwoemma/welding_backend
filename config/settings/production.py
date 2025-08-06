from .base import *
import os
import dj_database_url
import sys

# Security settings
DEBUG = True  # Change to False in production!
# SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-fallback-key-for-dev-only')
ALLOWED_HOSTS = [
    "welding-backend-vm1n.onrender.com",
    "welding-backend.onrender.com",
    "localhost",  # Add if needed for local development
]

# Database Configuration
# DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://welder_user:H8q6ped5s40EJLXLMgAanVnv2YOo1gRC@dpg-d29mkc6uk2gs73f6ofeg-a.frankfurt-postgres.render.com/welder_app_backend_db_4r6e')

# DATABASES = {
#     'default': dj_database_url.config(
#         default=DATABASE_URL,
#         conn_max_age=600,
#         ssl_require=True  # Important for Render.com
#     )
# }

# # Fallback to SQLite if no database configured (for local development only)
# if 'test' in sys.argv or not DATABASES['default']:
#     DATABASES['default'] = {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Authentication
AUTH_USER_MODEL = 'accounts.User'

# Logging configuration remains the same
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