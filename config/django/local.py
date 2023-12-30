from config.env import env
from config.django.base import *  # noqa

pymysql.install_as_MySQLdb()
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("LOCAL_MYSQL_DATABASE", default="jurin"),
        "USER": env("LOCAL_MYSQL_USER", default="root"),
        "PASSWORD": env("LOCAL_MYSQL_PASSWORD", default="password"),
        "HOST": env("LOCAL_MYSQL_HOST", default="localhost"),
        "PORT": env("LOCAL_MYSQL_PORT", default="3306"),
    }
}
