# query_params.py
# Copyright (C) 2021 Ben Tilley <targansaikhan@gmail.com>
#
# Distributed under terms of the MIT license.


CANDLE_SIZES = [
    "1m",
    "3m",
    "5m",
    "15m",
    "30m",
    "1H",
    "2H",
    "4H",
    "6H",
    "12H",
    "1D",
    "1W",
    "1M",
    "3M",
    "6M",
    "1Y",
]


class QueryParams(dict):
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            self.add_param(k, v)

    def add_param(self, key, value):
        if value is not None:
            if not hasattr(self, key):
                raise KeyError(f"QueryParams does not support {key}")
            self[key] = getattr(self, key)(value)

    def after(self, after):
        # assert is time stamp
        raise Exception("need to implements")

    def bar(self, candle_size):
        assert candle_size in CANDLE_SIZES
        return candle_size

    def before(self, before):
        # assert is time stamp
        raise Exception("need to implements")

    def ccy(self, currencies):
        return ",".join(currencies)

    def instType(self, instrument_type):
        return instrument_type

    def instId(self, instrument_id):
        if instrument_id is None:
            raise TypeError("You must provide an instrument_id")
        return instrument_id

    def limit(self, limit):
        assert isinstance(limit, int), "limit must be an integer"
        assert limit > 0, "limit must be greater than 0"
        return str(limit)
