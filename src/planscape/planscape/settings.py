"""
Specific Planscape settings can be overridden by the .env file.
These settings are

  SECRET_KEY:               Django key
  PLANSCAPE_DEBUG:          True or False

  PLANSCAPE_DATABASE_HOST: PostGIS hostname
  PLANSCAPE_DATABASE_NAME: PostGIS database name
  PLANSCAPE_DATABASE_USER: PostGIS user name
  PLANSCAPE_DATABASE_PASSWORD: PostGIS database password

  PLANSCAPE_ALLOWED_HOSTS:        Comma-separated string of addresses
  PLANSCAPE_CORS_ALLOWED_ORIGINS: Comma-separated string of addresses
  PLANSCAPE_CORS_ALLOWED_HOSTS:   Comma-separated string of addresses
  PLANSCAPE_CSRF_TRUSTED_ORIGINS: Comma-separated string of addresses

  PLANSCAPE_CACHE_BACKEND: Backend type for cache
  PLANSCAPE_CACHE_LOCATION: Cache location (important for memcached, etc.)
"""
import multiprocessing
import os
from pathlib import Path
import sentry_sdk
from corsheaders.defaults import default_headers
from decouple import config
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("PLANSCAPE_DEBUG", default=False, cast=bool)

ALLOWED_HOSTS: list[str] = str(config("PLANSCAPE_ALLOWED_HOSTS", default="*")).split(
    ","
)


# Application definition
planscape_apps = [
    "attributes",
    "boundary",
    "conditions",
    "planning",
    "stands",
    "users",
    "restrictions",
    "utils",
]
INSTALLED_APPS = [
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "corsheaders",
    "dj_rest_auth",
    "dj_rest_auth.registration",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "django_crontab",
    "leaflet",
    "lockdown",
    "password_policies",
    "rest_framework",
    "rest_framework_gis",
    "rest_framework_simplejwt",
    "rest_framework.authtoken",
] + planscape_apps

# Middleware order matters because of layering dependencies
# https://docs.djangoproject.com/en/4.2/topics/http/middleware/#activating-middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "password_policies.middleware.PasswordExpirationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "lockdown.middleware.LockdownMiddleware",
]

ROOT_URLCONF = "planscape.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(BASE_DIR, "templates"),
            os.path.join(BASE_DIR, "templates/allauth"),
        ],
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

WSGI_APPLICATION = "planscape.wsgi.application"

PLANSCAPE_DATABASE_HOST = config("PLANSCAPE_DATABASE_HOST", default="localhost")
PLANSCAPE_DATABASE_PASSWORD = config("PLANSCAPE_DATABASE_PASSWORD", default="pass")
PLANSCAPE_DATABASE_USER = config("PLANSCAPE_DATABASE_USER", default="planscape")
PLANSCAPE_DATABASE_NAME = config("PLANSCAPE_DATABASE_NAME", default="planscape")
PLANSCAPE_DATABASE_PORT = config("PLANSCAPE_PORT", default=5432)
DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "HOST": PLANSCAPE_DATABASE_HOST,
        "NAME": PLANSCAPE_DATABASE_NAME,
        "USER": PLANSCAPE_DATABASE_USER,
        "PASSWORD": PLANSCAPE_DATABASE_PASSWORD,
        "PORT": PLANSCAPE_DATABASE_PORT,
        "TEST": {
            "NAME": "auto_test",
        },
    }
}


# Locking down API calls to only itself.
LOCKDOWN_ENABLED = False

# if we ever needed to make some backend APIs (views) available to anyone.
LOCKDOWN_VIEW_EXCEPTIONS = []

# should put in all IPs matching planscape/trusted hosts
LOCKDOWN_REMOTE_ADDR_EXCEPTIONS = [
    "127.0.0.1",
    "::1",
]

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
    {
        "NAME": "users.reused_password_validator.CustomReusedPasswordValidator",
        "OPTIONS": {
            "record_length": 10,
        },
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = "static/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

SPATIALITE_LIBRARY_PATH = "/opt/homebrew/lib/mod_spatialite.dylib"

CORS_ALLOWED_ORIGINS = str(
    config("PLANSCAPE_CORS_ALLOWED_ORIGINS", default="http://localhost:4200")
).split(",")
CORS_ALLOWED_HOSTS = str(
    config("PLANSCAPE_CORS_ALLOWED_HOSTS", default="http://localhost:4200")
).split(",")
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = list(default_headers) + ["Set-Cookie"]

# Cross-Site Request Forgery protection settings
CSRF_USE_SESSIONS = False
CSRF_COOKIE_HTTPONLY = False
CSRF_TRUSTED_ORIGINS = str(
    config("PLANSCAPE_CSRF_TRUSTED_ORIGINS", default="http://localhost:4200")
).split(",")
CSRF_HEADER_NAME = "CSRF_COOKIE"
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = None
SESSION_COOKIE_SAMESITE = None

# True if a non-logged-in user can save plans.
PLANSCAPE_GUEST_CAN_SAVE = True

# Authentication settings (dj-rest-auth)

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
    ),
    "NON_FIELD_ERRORS_KEY": "global",
}

REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_COOKIE": "my-app-auth",
    "JWT_AUTH_REFRESH_COOKIE": "my-refresh-token",
    "JWT_AUTH_HTTPONLY": False,
    "REGISTER_SERIALIZER": "users.serializers.NameRegistrationSerializer",
    "OLD_PASSWORD_FIELD_ENABLED": True,
    "PASSWORD_CHANGE_SERIALIZER": "users.serializers.CustomPasswordChangeSerializer",
    "PASSWORD_RESET_SERIALIZER": "users.serializers.CustomPasswordResetSerializer",
    "PASSWORD_RESET_CONFIRM_SERIALIZER": "users.serializers.CustomPasswordResetConfirmSerializer",
    "LANGUAGE_CODE": "en-us",
}

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
]

# allauth

SITE_ID = 1
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_EMAIL_SUBJECT_PREFIX = "[Planscape] "
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_USERNAME_REQUIRED = False
LOGOUT_ON_PASSWORD_CHANGE = False
ACCOUNT_ADAPTER = "users.allauth_adapter.CustomAllauthAdapter"
PASSWORD_RESET_TIMEOUT = 1800  # 30 minutes.
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="smtp.google.com")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_PORT = config("EMAIL_PORT", cast=int, default=587)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", "no-reply@planscape.org")
EMAIL_HOST_PASSWORD = config("EMAIL_BACKEND_APP_PASSWORD", default="UNSET")
DEFAULT_FROM_EMAIL = "no-reply@planscape.org"

SESSION_REMEMBER = True
SESSION_COOKIE_AGE = 60 * 60 * 24 * 90  # 90 days
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

# PostGIS constants. All raster data should be ingested with a common
# Coordinate Reference System (CRS).  The values below are those for the
# Regional Resource Kits: the CRS code used for the rasters, and the proj4
# representation of that coordinate system.
CRS_FOR_RASTERS = 3857
CRS_9822_PROJ4 = (
    "+proj=aea +lat_0=23 +lon_0=-96 +lat_1=29.5 +lat_2=45.5 +x_0=0 +y_0=0 "
    "+datum=WGS84 +units=m +no_defs"
)
CRS_9822_SCALE = (300, -300)  # a raster transform has origin, scale, and skew.

# The area of a raster pixel (in km-squared).
RASTER_PIXEL_AREA = 0.300 * 0.300

# This is the default CRS used when a geometry is missing one.
DEFAULT_CRS = 4269

# Caching; this improves loading times especially for the boundary app.
CACHES = {
    "default": {
        "BACKEND": config(
            "PLANSCAPE_CACHE_BACKEND",
            default="django.core.cache.backends.locmem.LocMemCache",
        ),
        "LOCATION": config("PLANSCAPE_CACHE_LOCATION", "planscape-cache"),
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname}: {name}.{message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
    },
}


ENV = config("ENV", "dev")
SENTRY_DSN = config("SENTRY_DSN", None)
if SENTRY_DSN is not None:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        send_default_pii=True,
        environment=ENV,
        enable_tracing=True,
        profiles_sample_rate=0.1,
        traces_sample_rate=0.05,
    )

DEFAULT_CONDITIONS_FILE = config(
    "DEFAULT_CONDITIONS_FILE", BASE_DIR / "config" / "conditions.json"
)
DEFAULT_TREATMENTS_FILE = config(
    "DEFAULT_TREATMENTS_FILE", BASE_DIR / "config" / "treatment_goals.json"
)
RASTER_ROOT = config("RASTER_ROOT", "/mnt/gis/planscape")
RASTER_TILE = config("RASTER_TILE", "32x32")
GDAL_NUM_THREADS = config(
    "GDAL_NUM_THREADS", default=multiprocessing.cpu_count(), cast=int
)

FORSYS_PATCHMAX_SCRIPT = BASE_DIR / "rscripts" / "forsys.R"

# TODO: Move this to a conf file that R can read?
OUTPUT_DIR = BASE_DIR / "output"

DEFAULT_EST_COST_PER_ACRE = config("DEFAULT_EST_COST_PER_ACRE", 2470, cast=float)


# SINGLE QUEUE BEHAVIOR
USE_CELERY_FOR_FORSYS = config("USE_CELERY_FOR_FORSYS", False, cast=bool)

# CELERY
CELERY_BROKER_URL = config("CELERY_BROKER_URL", "redis://localhost:6379/0")

CELERY_RESULT_BACKEND = config("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_ACCEPT_CONTENT = ("json",)
# fetches ONE task at a time
CELERY_WORKER_PREFETCH_MULTIPLIER = config(
    "CELERY_WORKER_PREFETCH_MULTIPLIER", 1, cast=int
)
CELERY_WORKER_MAX_TASKS_PER_CHILD = config(
    "CELERY_WORKER_MAX_TASKS_PER_CHILD", 20, cast=int
)
CELERY_TASK_DEFAULT_QUEUE = "default"
# if not specified here it will be sent to the default queue
CELERY_TASK_ROUTES = {"planning.tasks.*": "forsys"}


SHARED_LINKS_NUM_DAYS_VALID = 60
CRONJOBS = [
    ("0 0 * * *", "planning.cron.delete_old_shared_links"),  # Runs at midnight daily
]
