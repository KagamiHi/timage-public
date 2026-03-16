import copy
import os
import sys
from datetime import timedelta
from pathlib import Path

import sentry_sdk
from django.conf import global_settings
from dotenv import load_dotenv

from common.utils.misc import random_str

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = os.environ.get("DEBUG", "0") == "1"
LOCAL = os.environ.get("LOCAL", "0") == "1"
COMMIT_HASH = os.environ.get("COMMIT_HASH", random_str(8))
BUILD_TAG = os.environ.get("BUILD_TAG", "local")

ALLOWED_HOSTS = ["*"]
EXTERNAL_HOST = os.environ["EXTERNAL_HOST"]

if not DEBUG:
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        environment=BUILD_TAG,
        send_default_pii=True,
    )

# Application definition
APPLICATIONS = [
    "bot",
    "common",
    "users",
]

SYSTEM_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_minio_backend",
    "django_celery_beat",
    "rest_framework",
    "rest_framework_simplejwt",
    "corsheaders",
]

INSTALLED_APPS = [
    *SYSTEM_APPS,
    *APPLICATIONS,
]

AUTH_USER_MODEL = "users.User"
AUTH_DELAY_THRESHOLD = timedelta(hours=1)

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

if LOCAL:
    MIDDLEWARE.append("common.middleware.LocalAuthMiddleware")
    CORS_ALLOW_ALL_ORIGINS = True

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "backend.wsgi.application"

# Database
DATABASES = dict(
    default=dict(
        ENGINE="django.db.backends.postgresql",
        NAME=os.environ["POSTGRES_DB"],
        USER=os.environ["POSTGRES_USER"],
        PASSWORD=os.environ["POSTGRES_PASSWORD"],
        HOST=os.environ["POSTGRES_HOST"],
        PORT=os.environ.get("POSTGRES_PORT", "5432"),
        CONN_HEALTH_CHECKS=True,
        ATOMIC_REQUESTS=True,
        OPTIONS={
            "pool": {
                "min_size": 5,
                "max_size": 20,
            }
        },
    )
)

REDIS_URL = os.environ["REDIS_URL"].rstrip("/")
CELERY_BROKER_URL = f"{REDIS_URL}/0"

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL,
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
        "KEY_PREFIX": "timage",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = "static/"
STATICFILES_DIRS = ["frontend/dist"]

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# MinIO
IMAGES_BUCKET = "images"
CDN_EXTERNAL_ENDPOINT = os.environ.get("CDN_EXTERNAL_ENDPOINT", "https://" + EXTERNAL_HOST + "/cdn")

STORAGES = copy.deepcopy(global_settings.STORAGES)
STORAGES.update(
    {
        "default": {
            "BACKEND": "django_minio_backend.models.MinioBackend",
            "OPTIONS": {
                "MINIO_ENDPOINT": os.environ["MINIO_ENDPOINT"],
                "MINIO_ACCESS_KEY": os.environ["MINIO_ROOT_USER"],
                "MINIO_SECRET_KEY": os.environ["MINIO_ROOT_PASSWORD"],
                "MINIO_USE_HTTPS": False,
                "MINIO_PUBLIC_BUCKETS": [IMAGES_BUCKET],
                "MINIO_BUCKET_CHECK_ON_SAVE": True,
            },
        },
    }
)

# Telegram bot
TLG_BOT_TOKEN = os.environ["BOT_TOKEN"]
TLG_LONG_POLLING = os.environ.get("DEBUG", "0") == "1"
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"]
TLG_API_ID = os.environ["API_ID"]
TLG_API_HASH = os.environ["API_HASH"]
TLG_SESSION_NAME = os.environ["SESSION_NAME"]

# Recommendations
DEFAULT_USER_RECOMMENDATION_RATIO = float(
    os.environ.get("DEFAULT_USER_RECOMMENDATION_RATIO", "0.7")
)

if "test" in sys.argv:
    import warnings
    warnings.filterwarnings("ignore", "No directory at")
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}
    CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "bot": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "aiogram": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}
