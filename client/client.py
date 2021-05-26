# client.py
# Copyright (C) 2021 Ben Tilley <targansaikhan@gmail.com>
#
# Distributed under terms of the MIT license.


from .api import OkexApi
from .api_models import CandleStick


class OkexClient(OkexApi):
    def get_candlesticks(self, **query_params):
        response = super().get_candlesticks(**query_params)
        data = response["data"]
        return list(map(CandleStick.from_api_data, data))
