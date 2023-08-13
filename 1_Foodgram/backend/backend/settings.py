import os
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfbase.ttfonts import TTFont

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG") == "True"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS").split()
CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS").split()

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "recipes.apps.RecipesConfig",
    "users.apps.UsersConfig",
    "api.apps.ApiConfig",
    "rest_framework",
    "rest_framework.authtoken",
    "djoser",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

if os.getenv("SQLITE") == "True":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("POSTGRES_DB", "postgres"),
            "USER": os.getenv("POSTGRES_USER", "admin"),
            "PASSWORD": os.getenv("POSTGRES_PASSWORD", "admin"),
            "HOST": os.getenv("DB_HOST", ""),
            "PORT": os.getenv("DB_PORT", 5432),
        }
    }


# Password validation

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
]


# Internationalization

LANGUAGE_CODE = "ru"

TIME_ZONE = "Europe/Moscow"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Default primary key field type

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# User model

AUTH_USER_MODEL = "users.User"

# Rest framework

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
}

# Djoser

DJOSER = {
    "LOGIN_FIELD": "email",
}

# Models

MAX_LENGTH_NAME = 200
MAX_LENGTH_UNIT = 200
MAX_LENGTH_SLUG = 200
MAX_LENGTH_COLOR = 7

MAX_INGREDIENT_AMOUNT = 32000
MIN_INGREDIENT_AMOUNT = 1
MAX_COOKING_TIME = 32000
MIN_COOKING_TIME = 1

MAX_LENGTH_STR = 30

# Users

MAX_LENGTH_EMAIL = 254
MAX_LENGTH_USERNAME = 150
MAX_LENGTH_FIRST_NAME = 150
MAX_LENGTH_LAST_NAME = 150
MAX_LENGTH_PASSWORD = 150

# Admin site

RECENT_RECIPES_LIMIT = 6

# Download shopping cart

PAGE_SIZE = letter

FONT_NAME = "MarckScript-Regular"
FONT_PATH = Path(Path.cwd(), "data", "fonts", "MarckScript-Regular.ttf")
pdfmetrics.registerFont(TTFont(FONT_NAME, FONT_PATH, "UTF-8"))

TITLE_TEXT = "Foodgram"
TITLE_FONT_SIZE = 70
TITLE_X_POSITION = 170
TITLE_Y_POSITION = PAGE_SIZE[1] - 70
TITLE_WIDTH = stringWidth(TITLE_TEXT, FONT_NAME, TITLE_FONT_SIZE)

CONTENT_FONT_SIZE = 24
CONTENT_X_POSITION = 40
CONTENT_Y_POSITION = PAGE_SIZE[1] - 130

FOOTER_FONT_SIZE = 19
FOOTER_FIRST_TEXT = "Все ваши рецепты в одном месте!"
FOOTER_FIRST_X_POSITION = 170
FOOTER_FIRST_Y_POSITION = 55

FOOTER_SECOND_TEXT = "myfoodgram.myvnc.com"
FOOTER_SECOND_X_POSITION = 230
FOOTER_SECOND_Y_POSITION = 30

UNDERLINE_WIDTH = 2
FIRST_UNDERLINE_X1_POSITION = 170
FIRST_UNDERLINE_Y1_POSITION = PAGE_SIZE[1] - 85
FIRST_UNDERLINE_X2_POSITION = 305
FIRST_UNDERLINE_Y2_POSITION = PAGE_SIZE[1] - 85

SECOND_UNDERLINE_X1_POSITION = 335
SECOND_UNDERLINE_Y1_POSITION = PAGE_SIZE[1] - 85
SECOND_UNDERLINE_X2_POSITION = TITLE_WIDTH + 170
SECOND_UNDERLINE_Y2_POSITION = PAGE_SIZE[1] - 85
