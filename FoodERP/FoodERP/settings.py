"""
Django settings for FoodERP project.
Generated by 'django-admin startproject' using Django 4.0.4.
For more information on this file, see
https://docs.djangoproject.com/en/4.0/topics/settings/
  
For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.0/ref/settings/
"""
from datetime import timedelta
import os 
from pathlib import Path


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-t#s!16-8)sy91!+@q2hmdt_yclkuldlx=*g5aw_cb&^+rzr@ty'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost','10.1.201.19','103.135.203.145','192.168.1.114','117.248.109.234','10.4.5.65','cbmfooderp.com','10.4.5.64','127.0.0.1'] 

# Application definition
CORS_ORIGIN_ALLOW_ALL = True #we allow the all domain to access through API
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'FoodERPApp.apps.FooderpappConfig',
    # 'activity_log',
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
    # 'activity_log.middleware.ActivityLogMiddleware',
]

ROOT_URLCONF = 'FoodERP.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # 'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


WSGI_APPLICATION = 'FoodERP.wsgi.application'
# For writing log to another DB

# DATABASE_ROUTERS = ['activity_log.router.DatabaseAppsRouter']
# DATABASE_APPS_MAPPING = {'activity_log': 'logs'}

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'FoodERP',     
        'USER': 'pk',
        'PASSWORD': 'P@ssw0rd',  
        'HOST': '10.4.5.64',
        'PORT': '3306' , 
        'OPTIONS': { 
            'sql_mode': 'STRICT_TRANS_TABLES', 
        },
    },
    
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME': 'transactionlogdb',
    #     'USER': 'pk',
    #     'PASSWORD': 'P@ssw0rd', 
    #     'HOST': '192.168.1.114',
    #     'PORT': '3306'
    # }

}

# SESSION_ENGINE = 'django.contrib.sessions.backends.db'
# SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# ACTIVITYLOG_AUTOCREATE_DB = True
# # Log anonymous actions?
# ACTIVITYLOG_ANONYMOUS = True
# # Update last activity datetime in user profile. Needs updates for user model.
# ACTIVITYLOG_LAST_ACTIVITY = True

# # Only this methods will be logged
# ACTIVITYLOG_METHODS = ('POST', 'GET','PUT','DELETE')

# # List of response statuses, which logged. By default - all logged.
# # Don't use with ACTIVITYLOG_EXCLUDE_STATUSES
# ACTIVITYLOG_STATUSES = (200, )

# # List of response statuses, which ignores. Don't use with ACTIVITYLOG_STATUSES
# # ACTIVITYLOG_EXCLUDE_STATUSES = (302, )

# # URL substrings, which ignores
# #ACTIVITYLOG_EXCLUDE_URLS = ('/admin/activity_log/activitylog', )
# ACTIVITYLOG_GET_EXTRA_DATA = 'FoodERPApp.models.make_extra_data'
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

TIME_ZONE = 'Asia/Calcutta'

USE_I18N = True

USE_TZ = False

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

# MEDIA_URL = '/home/admin1/DeepManthan/FoodERP/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_USE_SSL = False
EMAIL_HOST_USER = 'support.mis@chitalegroup.in'
EMAIL_HOST_PASSWORD = 'zebydcaqvmsfwujb'

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'FoodERPApp.M_Users' 
REST_FRAMEWORK = {
     'DEFAULT_PERMISSION_CLASSES': [
         'rest_framework.permissions.IsAuthenticated',
         'rest_framework.permissions.IsAdminUser',
         ],
    'DEFAULT_AUTHENTICATION_CLASSES': (
    #  'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
     'rest_framework.authentication.SessionAuthentication',
     'rest_framework_simplejwt.authentication.JWTAuthentication',
     )
}



# Jwt Authentication

# JWT_AUTH = {
#     'JWT_ENCODE_HANDLER':
#     'rest_framework_jwt.utils.jwt_encode_handler',

#     'JWT_DECODE_HANDLER':
#     'rest_framework_jwt.utils.jwt_decode_handler',

#     'JWT_PAYLOAD_HANDLER':
#     'rest_framework_jwt.utils.jwt_payload_handler',

#     'JWT_PAYLOAD_GET_USER_ID_HANDLER':
#     'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',

#     'JWT_RESPONSE_PAYLOAD_HANDLER':
#     'rest_framework_jwt.utils.jwt_response_payload_handler',

#     'JWT_SECRET_KEY': 'SECRET_KEY',
#     'JWT_GET_USER_SECRET_KEY': None,
#     'JWT_PUBLIC_KEY': None,
#     'JWT_PRIVATE_KEY': None,
#     'JWT_ALGORITHM': 'HS256',
#     'JWT_VERIFY': True,
#     'JWT_VERIFY_EXPIRATION': True,
#     'JWT_LEEWAY': 0,
#     # 'JWT_EXPIRATION_DELTA': timedelta(minutes=1),
#     'JWT_EXPIRATION_DELTA': timedelta(days=30),

#     'JWT_AUDIENCE': None,
#     'JWT_ISSUER': None,

#     'JWT_ALLOW_REFRESH': False,
#     'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=30),

#     'JWT_AUTH_HEADER_PREFIX': 'Bearer',
#     'JWT_AUTH_COOKIE': None,

#     'JWT_PAYLOAD_HANDLER':
#     'rest_framework_jwt.utils.jwt_payload_handler',

# }
SIMPLE_JWT = {

    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=120),

    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    # "SIGNING_KEY": settings.SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",), 
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "SLIDING_TOKEN_REFRESH_EXP_CLAIM": "refresh_exp",
    "SLIDING_TOKEN_LIFETIME": timedelta(minutes=5),
    "SLIDING_TOKEN_REFRESH_LIFETIME": timedelta(days=1),

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}
