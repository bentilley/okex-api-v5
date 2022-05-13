# client.py
# Copyright (C) 2021 Ben Tilley <targansaikhan@gmail.com>
#
# Distributed under terms of the MIT license.


from .api import OkexApi
from .api_models import CandleStick, OrderBook, Trade


class OkexClient(OkexApi):
    def get_candlesticks(self, **query_params):
        response = super().get_candlesticks(**query_params)
        data = response["data"]
        return list(map(CandleStick.from_api_data, data))

    def get_candlesticks_history(self, **query_params):
        response = super().get_candlesticks_history(**query_params)
        data = response["data"]
        return list(map(CandleStick.from_api_data, data))

    def get_order_book(self, **query_params):
        response = super().get_order_book(**query_params)
        data = response["data"]
        return OrderBook.from_api_data(data[0])

    def get_trades(self, **query_params):
        response = super().get_trades(**query_params)
        data = response["data"]
        return list(map(Trade.from_api_data, data))
