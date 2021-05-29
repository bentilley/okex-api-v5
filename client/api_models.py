# api_models.py
# Copyright (C) 2021 Ben Tilley <targansaikhan@gmail.com>
#
# Distributed under terms of the MIT license.


from datetime import datetime
from functools import cached_property
from typing import Any, Dict, List
from dataclasses import dataclass


class ModelTimestampMixin:
    """Base class for API data wrappers with timestamps.

    The timestamp is the millisecond format of the POSIX timestamp, this means
    that to get the number of seconds we need to be dividing by 1000.
    """

    _timestamp: str

    @cached_property
    def timestamp(self) -> datetime:
        # timestamp is in milliseconds -> divide by 1000 to get seconds
        return datetime.fromtimestamp(float(self._timestamp) / 1000)


@dataclass
class CandleStick(ModelTimestampMixin):
    """Simple wrapper for candlestick data.

    This is initialised from OKEX API data from candlestick returning endpoints.

    Args:
        timestamp: millisecond format of Unix timestamp
        open: open price of the period
        high: high price of the period
        low: low price of the period
        close: close price of the period
        volumne: volatility of the period in contracts
        volumne_in_currency: volatility of the period in currency
    """

    _timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    volume_in_currency: float

    @staticmethod
    def from_api_data(api_data: List[str]) -> "CandleStick":
        [ts, o, h, l, c, vol, vol_currency] = api_data
        return CandleStick(
            ts, float(o), float(h), float(l), float(c), float(vol), float(vol_currency)
        )

    @cached_property
    def change(self):
        return round(self.close - self.open, 1)

    @cached_property
    def spread(self):
        return round(self.high - self.low, 1)


@dataclass
class Trade(ModelTimestampMixin):
    """Simple wrapper for trade data.

    This is initialised from OKEX API data from trades returning endpoints.

    Args/Returns/Raises:
        example: Brief explanation
    """

    instrument_id: str
    price: float
    side: str
    size: float
    trade_id: str
    _timestamp: str

    @staticmethod
    def from_api_data(api_data: Dict[str, Any]) -> "Trade":
        return Trade(
            api_data["instId"],
            float(api_data["px"]),
            api_data["side"],
            float(api_data["sz"]),
            api_data["tradeId"],
            api_data["ts"],
        )
