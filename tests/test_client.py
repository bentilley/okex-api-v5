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
