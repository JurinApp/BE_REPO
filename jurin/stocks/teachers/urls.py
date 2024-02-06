from django.urls import path

from jurin.stocks.teachers.apis import (
    TeacherStockDetailAPI,
    TeacherStockListAPI,
    TeacherStockTodayTradeListAPI,
)

urlpatterns = [
    path("", TeacherStockListAPI.as_view(), name="teacher-stock-list"),
    path("/today-trade", TeacherStockTodayTradeListAPI.as_view(), name="teacher-stock-today-trade-list"),
    path("/<int:stock_id>", TeacherStockDetailAPI.as_view(), name="teacher-stock-detail"),
]
