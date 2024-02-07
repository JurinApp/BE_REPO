from django.urls import path

from jurin.stocks.students.apis import (
    StudentMyStockDetailAPI,
    StudentMyStockListAPI,
    StudentMyStockTradeInfoListAPI,
    StudentStockDetailAPI,
    StudentStockListAPI,
    StudentStockTradeListAPI,
    StudentStockTradeTodayListAPI,
)

urlpatterns = [
    path("", StudentStockListAPI.as_view(), name="student-stock-list"),
    path("/trades/today", StudentStockTradeTodayListAPI.as_view(), name="student-stock-trade-today-list"),
    path("/mine", StudentMyStockListAPI.as_view(), name="student-stock-mine-list"),
    path("/<int:stock_id>", StudentStockDetailAPI.as_view(), name="student-stock-detail"),
    path("/<int:stock_id>/mine", StudentMyStockDetailAPI.as_view(), name="student-stock-detail-mine"),
    path("/<int:stock_id>/trades/mine", StudentMyStockTradeInfoListAPI.as_view(), name="student-stock-trade-info-mine-list"),
    path("/<int:stock_id>/trades", StudentStockTradeListAPI.as_view(), name="student-stock-trade-today-list"),
]
