from django.contrib import admin

from jurin.users.models import User, VerificationCode

admin.site.register(VerificationCode)
admin.site.register(User)
