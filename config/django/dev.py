from config.env import env
from config.django.base import *  # noqa

SECRET_KEY = env("SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = ["*"]

pymysql.install_as_MySQLdb()
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("DEV_MYSQL_DATABASE"),
        "USER": env("DEV_MYSQL_USER"),
        "PASSWORD": env("DEV_MYSQL_PASSWORD"),
        "HOST": env("DEV_MYSQL_HOST"),
        "PORT": env("DEV_MYSQL_PORT"),
    }
}

SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=True)

# https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# https://docs.djangoproject.com/en/dev/ref/settings/#secure-ssl-redirect
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)
# https://docs.djangoproject.com/en/dev/ref/middleware/#x-content-type-options-nosniff
SECURE_CONTENT_TYPE_NOSNIFF = env.bool("SECURE_CONTENT_TYPE_NOSNIFF", default=True)
