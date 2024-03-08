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
    path("", StudentStockListAPI.as_view(), name="student_stock_list"),
    path("/trades/today", StudentStockTradeTodayListAPI.as_view(), name="student_stock_trade_today_list"),
    path("/mine", StudentMyStockListAPI.as_view(), name="student_stock_mine_list"),
    path("/<int:stock_id>", StudentStockDetailAPI.as_view(), name="student_stock_detail"),
    path("/<int:stock_id>/mine", StudentMyStockDetailAPI.as_view(), name="student_stock_detail_mine"),
    path("/<int:stock_id>/trades/mine", StudentMyStockTradeInfoListAPI.as_view(), name="student_stock_trade_info_mine_list"),
    path("/<int:stock_id>/trades", StudentStockTradeListAPI.as_view(), name="student_stock_trade_today_list"),
]
