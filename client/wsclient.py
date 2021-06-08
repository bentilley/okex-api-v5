# wsclient.py
# Copyright (C) 2021 Ben Tilley <targansaikhan@gmail.com>
#
# Distributed under terms of the MIT license.


from .ws import OkexWebsocketsApi
from .api_models import Trade


class OkexWebsocketsClient(OkexWebsocketsApi):
    async def trades(self, instrument_id: str):
        async for trade_data in super().trades(instrument_id=instrument_id):
            yield Trade.from_api_data(trade_data)
