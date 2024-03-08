from django.contrib import admin

from jurin.stocks.models import DailyPrice, Stock, UserStock, UserTradeInfo

admin.site.register(Stock)
admin.site.register(UserStock)
admin.site.register(DailyPrice)
admin.site.register(UserTradeInfo)
