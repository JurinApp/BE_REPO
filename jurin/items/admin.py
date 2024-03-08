from django.contrib import admin

from jurin.items.models import Item, UserItem, UserItemLog

admin.site.register(Item)
admin.site.register(UserItem)
admin.site.register(UserItemLog)
