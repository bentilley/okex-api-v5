# test_ws.py
# Copyright (C) 2021 Ben Tilley <targansaikhan@gmail.com>
#
# Distributed under terms of the MIT license.


import asyncio
from datetime import datetime


class TestOkexWebSocketsApi:
    def test_trades(self, ws_api):
        async def test():
            async for trade in ws_api.trades(instrument_id="BTC-USDT"):
                assert isinstance(trade.timestamp, datetime)
                assert isinstance(trade.instrument_id, str)
                assert isinstance(trade.price, float)
                assert isinstance(trade.side, str)
                assert isinstance(trade.size, float)
                assert isinstance(trade.trade_id, str)
                break

        asyncio.run(test())
