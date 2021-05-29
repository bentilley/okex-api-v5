# test_client.py
# Copyright (C) 2021 Ben Tilley <targansaikhan@gmail.com>
#
# Distributed under terms of the MIT license.


import pytest
from datetime import datetime


class TestOkexClient:
    def test_private_endpoint(self, client):
        data = client.get_account_balance()
        assert data

    @pytest.mark.vcr()
    def test_get_candlesticks(self, client):
        candlesticks = client.get_candlesticks(instrument_id="XCH-USDT", limit=5)
        assert len(candlesticks) == 5
        for candlestick in candlesticks:
            assert isinstance(candlestick.timestamp, datetime)
            assert isinstance(candlestick.open, float)
            assert isinstance(candlestick.high, float)
            assert isinstance(candlestick.low, float)
            assert isinstance(candlestick.close, float)
            assert isinstance(candlestick.volume, float)
            assert isinstance(candlestick.volume_in_currency, float)

    @pytest.mark.vcr()
    def test_get_order_book(self, client):
        order_book = client.get_order_book(instrument_id="ETH-USDT", book_depth=5)
        assert isinstance(order_book.timestamp, datetime)
        assert len(order_book.asks) == 5
        assert len(order_book.bids) == 5
        for order in order_book.asks + order_book.bids:
            assert isinstance(order.price, float)
            assert isinstance(order.size, float)
            assert isinstance(order.num_liquidated_orders, int)
            assert isinstance(order.num_orders, int)

    @pytest.mark.vcr()
    def test_get_trades(self, client):
        trades = client.get_trades(instrument_id="BTC-USDT", limit=5)
        assert len(trades) == 5
        for trade in trades:
            assert isinstance(trade.instrument_id, str)
            assert isinstance(trade.timestamp, datetime)
            assert isinstance(trade.price, float)
            assert trade.side == "sell" or trade.side == "buy"
            assert isinstance(trade.size, float)
            assert isinstance(trade.trade_id, str)
