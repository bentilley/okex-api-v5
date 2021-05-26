# test_client.py
# Copyright (C) 2021 Ben Tilley <targansaikhan@gmail.com>
#
# Distributed under terms of the MIT license.


# import json
import os
import pytest
from client import OkexClient


@pytest.fixture
def api_key():
    return os.getenv("OKEX_API_KEY")


@pytest.fixture
def passphrase():
    return os.getenv("OKEX_PASSPHRASE")


@pytest.fixture
def secretkey():
    return os.getenv("OKEX_SECRET_KEY")


@pytest.fixture
def client(api_key, passphrase, secretkey):
    return OkexClient(api_key=api_key, passphrase=passphrase, secretkey=secretkey)


class TestOkexClient:
    def test_public_endpoint(self, client):
        data = client.get_tickers()
        assert data

    def test_private_endpoint(self, client):
        data = client.get_account_balance()
        assert data

    def test_get_candlesticks(self, client):
        candlesticks = client.get_candlesticks(instrument_id="XCH-USDT", limit="5")
        assert len(candlesticks) == 5
        for candlestick in candlesticks:
            assert candlestick.instrument_id == "XCH-USDT"
            assert isinstance(candlestick.timestamp, int)
            assert isinstance(candlestick.open, float)
            assert isinstance(candlestick.highest, float)
            assert isinstance(candlestick.lowest, float)
            assert isinstance(candlestick.close, float)
            assert isinstance(candlestick.volume, int)
            assert isinstance(candlestick.volumne_currency, float)
