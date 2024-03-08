from django.contrib import admin

from jurin.channels.models import Channel, UserChannel

admin.site.register(Channel)
admin.site.register(UserChannel)
