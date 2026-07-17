
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")


if os.getenv("local_db") is None:
    DEBUG =  False
else:
    DEBUG =  True



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'api',
    'api_version_2'
    
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    "corsheaders.middleware.CorsMiddleware",#for cors header
    "django.middleware.common.CommonMiddleware",#for cors header
    "django.middleware.security.SecurityMiddleware", # diaplying static files
    "whitenoise.middleware.WhiteNoiseMiddleware", # diaplying static files
]

ROOT_URLCONF = 'lecture_tracker_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'api' / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'lecture_tracker_backend.wsgi.application'

if os.getenv("local_db") is None:
    DATABASES = {
         'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME'),
            'USER': os.getenv('DB_USER'),
            'PASSWORD': os.getenv('DB_PASSWORD'),
            'HOST': os.getenv('DB_HOST'),
            'PORT': os.getenv('DB_PORT'),
            'OPTIONS': {
                'sslmode': 'require',
    
            },
        }
    }
else:
    DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

STATIC_ROOT = BASE_DIR / 'staticfiles' #for whitenoise


ALLOWED_HOSTS =  [".vercel.app", "127.0.0.1", "esta-sensate-unquickly.ngrok-free.dev", 'localhost']
# CORS_ALLOW_ALL_ORIGINS = True

#smtp usage
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_SSL = True
EMAIL_HOST_USER = 'lastissa11@gmail.com'
EMAIL_HOST_PASSWORD = os.getenv('GMAIL_PASSWORD')
DEFAULT_FROM_EMAIL = 'lastissa11@gmail.com'
EMAIL_PORT = 465


#background task queue - redis as the chef and celery as the receipt collector
CELERY_BROKER_URL = os.getenv("REDIS_URL")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"

#redis cache system
if os.getenv("local_db") is None:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": CELERY_BROKER_URL,
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": 'django.core.cache.backends.locmem.LocMemCache',
            "LOCATION": CELERY_BROKER_URL,
        }
    }
