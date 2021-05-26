# api_models.py
# Copyright (C) 2021 Ben Tilley <targansaikhan@gmail.com>
#
# Distributed under terms of the MIT license.


from datetime import datetime
from functools import cached_property
from typing import List


class CandleStick:
    """Simple wrapper for candlestick data.

    This is initialised from OKEX API data from candlestick reurning endpoints.

    Note that the timestap is a weird format. It is the millisecond format of
    the POSIX timestamp, this means that to get the number of seconds we need
    to be dividing by 1000.

    Args:
        timestamp: millisecond format of Unix timestamp
        open: open price of the period
        high: high price of the period
        low: low price of the period
        close: close price of the period
        volumne: volatility of the period in contracts
        volumne_in_currency: volatility of the period in currency
    """

    def __init__(
        self,
        timestamp: str,
        open: float,
        high: float,
        low: float,
        close: float,
        volume: float,
        volume_in_currency: float,
    ):
        # timestamp is in milliseconds -> divide by 1000 to get seconds
        self.timestamp = datetime.fromtimestamp(float(timestamp) / 1000)
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        self.volume = volume
        self.volume_in_currency = volume_in_currency

    @staticmethod
    def from_api_data(api_data: List[str]) -> "CandleStick":
        [ts, o, h, l, c, vol, vol_currency] = api_data
        return CandleStick(
            ts, float(o), float(h), float(l), float(c), float(vol), float(vol_currency)
        )

    def __repr__(self):
        return (
            f"<CandleStick ts:{self.timestamp} "
            f"o:{self.open} h:{self.high} l:{self.low} c:{self.close}>"
        )

    @cached_property
    def change(self):
        return round(self.close - self.open, 1)

    @cached_property
    def spread(self):
        return round(self.high - self.low, 1)
