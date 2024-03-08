from django.urls import path

from jurin.stocks.teachers.apis import (
    TeacherStockDetailAPI,
    TeacherStockListAPI,
    TeacherStockTradeTodayListAPI,
)

urlpatterns = [
    path("", TeacherStockListAPI.as_view(), name="teacher_stock_list"),
    path("/trades/today", TeacherStockTradeTodayListAPI.as_view(), name="teacher_stock_trade_today_list"),
    path("/<int:stock_id>", TeacherStockDetailAPI.as_view(), name="teacher_stock_detail"),
]
