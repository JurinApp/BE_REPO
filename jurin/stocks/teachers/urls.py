from django.urls import path

from jurin.stocks.teachers.apis import (
    TeacherStockDetailAPI,
    TeacherStockListAPI,
    TeacherStockTradeTodayListAPI,
)

urlpatterns = [
    path("", TeacherStockListAPI.as_view(), name="teacher-stock-list"),
    path("/trades/today", TeacherStockTradeTodayListAPI.as_view(), name="teacher-stock-trade-today-list"),
    path("/<int:stock_id>", TeacherStockDetailAPI.as_view(), name="teacher-stock-detail"),
]
