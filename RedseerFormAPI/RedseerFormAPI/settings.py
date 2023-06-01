"""
Django settings for RedseerFormAPI project.

Generated by 'django-admin startproject' using Django 4.0.1.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""

from pathlib import Path
import pymysql
import os
import dj_database_url
from urllib.parse import quote
from dotenv import load_dotenv
load_dotenv()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-9ioop*7+s^+7^mg)k41=7r1+ml!h_ow_943!8m!-_upzjl**hv'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = (os.getenv('DEBUG', 'True') == 'True')

ALLOWED_HOSTS = ['*']

# Danjgo Admin uses below two parameter for Cross Site Request Forgery(CSRF) verification for trusted origins
CSRF_TRUSTED_ORIGINS = [
    'https://testwebformapi.benchmarks.digital',
    'https://webformapi.benchmarks.digital'
]
CSRF_COOKIE_SECURE = True


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'django_apscheduler',
    'FormAPI'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'RedseerFormAPI.middleware.CorsMiddleware'
]

ROOT_URLCONF = 'RedseerFormAPI.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'RedseerFormAPI.wsgi.application'
CORS_ALLOW_ALL_ORIGINS = True

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# get the value of the DATABASE_URL environment variable
db_url = os.getenv('DATABASE_URL')
print("DATABASE_URL =", db_url)

# if the DATABASE_URL not passed, raise error
if not db_url:
    raise Exception(
        "Error, DATABASE_URL is not passed, required format is => mysql://user:pass@localhost:3000/dbname")

# quote is used to encode special charactor like #, except :/@
# then parse is used to handle encoded url
# for url without special charactors only dj_database_url.config could have been used
DATABASES = {
    'default': dj_database_url.parse(quote(db_url, ':/@'))
    # 'default': dj_database_url.config(db_url)
}

# Old DB connection
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': 'content_data',
#         'USER': 'redroot',
#         'PASSWORD': 'seer#123',
#         'HOST': 'redmysql.mysql.database.azure.com',
#         'PORT': '3306',
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

# where the static files will be served from
STATIC_URL = '/staticfiles/'
# where the static files will be collected to
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media_root")
# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
pymysql.install_as_MySQLdb()


EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
print("EMAIL_BACKEND =", EMAIL_BACKEND)

EMAIL_HOST = os.getenv('EMAIL_HOST')
print("EMAIL_HOST =", EMAIL_HOST)
if not EMAIL_HOST:
    raise Exception("Error, EMAIL_HOST is not passed")

EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
print("EMAIL_HOST_USER =", EMAIL_HOST_USER)
if not EMAIL_HOST_USER:
    raise Exception("Error, EMAIL_HOST_USER is not passed")

EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
print("EMAIL_HOST_PASSWORD =", EMAIL_HOST_PASSWORD)
if not EMAIL_HOST_PASSWORD:
    raise Exception("Error, EMAIL_HOST_PASSWORD is not passed")

EMAIL_USE_TLS = (os.getenv('EMAIL_USE_TLS', 'True') == 'True')
print("EMAIL_USE_TLS =", EMAIL_USE_TLS)

MAIL_SUBJECT_SUFFIX = " - Test Environment" if os.getenv(
            "MY_APP_ENV") == "test" else ""

DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
