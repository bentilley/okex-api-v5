# __init__.py
# Copyright (C) 2021 Ben Tilley <targansaikhan@gmail.com>
#
# Distributed under terms of the MIT license.


import os
import base64
from datetime import datetime
import hmac
import hashlib
import json
import logging
import requests
from typing import Dict, List, Optional

from .query_params import QueryParams

logger = logging.getLogger(__name__)


class OkexApi:
    """API client for the OKEX crypto trading platform.

    Go to https://www.okex.com/account/my-api to create an API key for your
    account. Use the details generated to instantiate a client in order to
    start making requests to the API. You don't need to provide a secret key is
    you are are only making requests to public endpoints.

    See the OKEX documentation for more information:
    https://www.okex.com/docs-v5/en/

    Args:
        api_key: The API key that you create in your OKEX account.
        passphrase: The passphrase that you gave the API key.
        secretkey: The secret key that was generated when you created the API key.
        base_url: The domain of the OKEX API.
    """

    def __init__(
        self,
        api_key: Optional[str] = os.getenv("OKEX_API_KEY"),
        passphrase: Optional[str] = os.getenv("OKEX_PASSPHRASE"),
        secretkey: Optional[str] = os.getenv("OKEX_SECRET_KEY"),
        base_url: str = "www.okex.com",
    ):
        if secretkey is None:
            logger.warning("Client does not have a secret key")

        if api_key is None:
            raise ValueError("OkexClient must have an api_key")
        if passphrase is None:
            raise ValueError("OkexClient must have a passphrase")

        self.api_key = api_key
        self.passphrase = passphrase
        self.secretkey = secretkey
        self.base_url = base_url
        self.protocol = "https"
        logger.info("OKEX Client Initialised")

    def compile_url(self, request_path: str) -> str:
        """Create a full URI from a request path.

        Args:
            request_path: The path of the request URL.
        """
        return f"{self.protocol}://{self.base_url}{request_path}"

    @staticmethod
    def compile_query_string(query_params: Dict[str, str]) -> str:
        """Compile a query string from a dictionary of parameters.

        Args:
            query_params: Query string parameters.
        """
        query_string = "?"
        for i, (k, v) in enumerate(query_params.items()):
            query_string += f"{'&' if i > 0 else ''}{k}={v}"
        return query_string

    @staticmethod
    def get_timestamp() -> str:
        """Get OKEX formatted timestamp for now.

        The OKEX formatting requires only 3 digits in the microseconds
        position. And for the timestamp to be terminated with a 'Z'.
        """
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"

    @staticmethod
    def get_signature(
        secretkey: str, time_stamp: str, method: str, request_path: str, body: str
    ) -> str:
        """Get the signature hash to sign the request.

        This implements the authentication algorithm found in the OKEX API
        docs: https://www.okex.com/docs-v5/en/?python#rest-api-authentication

        Args:
            time_stamp: Time stamp of when the request is being made.
            method: The HTTP method e.g. "GET", "POST", etc.
            request_path: The path of the request URL.
            body: The stringified body of the request with no whitespace.
        """
        prehash = time_stamp + method.upper() + request_path + body
        logger.debug(f"Computing signature from prehash: {prehash}")

        h = hmac.new(
            bytes(secretkey, "ascii"), bytes(prehash, "ascii"), hashlib.sha256
        ).digest()
        base64_encoded = base64.b64encode(h).decode("ascii")
        return base64_encoded

    def get_headers(self, method: str, request_path: str, body: str) -> Dict[str, str]:
        """Get the required headers for a request.

        Args:
            method: The HTTP method e.g. "GET", "POST", etc.
            request_path: The path of the request URL.
            body: The stringified body of the request with no whitespace.
        """
        if self.secretkey is None:
            return {}

        time_stamp = self.get_timestamp()
        signature = self.get_signature(
            self.secretkey, time_stamp, method, request_path, body
        )
        headers = {
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": time_stamp,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
        }
        return headers

    def make_request(
        self,
        method: str,
        request_path: str,
        query_params: Optional[Dict[str, str]] = None,
        **params: Dict[str, str],
    ) -> Dict:
        """Make a signed request to the OKEX API.

        We handle query params ourselves, because we need to include them in
        the sign generation.

        Args:
            method: The HTTP method e.g. "GET", "POST", etc.
            request_path: The path of the request URL.
            query_params: Query string parameters.
            params: Remaining kwargs make up the request body.
        """
        body = json.dumps(params, separators=(",", ":")) if params else ""
        _method = getattr(requests, method.lower())

        if query_params:
            request_path += self.compile_query_string(query_params)

        response = _method(
            self.compile_url(request_path),
            headers=self.get_headers(method, request_path, body),
        )
        return response.json()

    def get(
        self, request_path: str, query_params: Optional[Dict[str, str]] = None
    ) -> Dict:
        """Perform a GET request."""
        return self.make_request("GET", request_path, query_params=query_params)

    def get_account_balance(self, currencies: Optional[List[str]] = None) -> Dict:
        """Get summary of account balance for different currencies.

        Specifying multiple currencies returns a separate summary for each
        asset class.

        Args:
            currencies: currencies to fetch balance for.
        """
        q = QueryParams(ccy=currencies)
        return self.get("/api/v5/account/balance", query_params=q)

    def get_tickers(
        self, instrument_type: str = "SPOT", underlying: Optional[str] = None
    ) -> Dict:
        """Get summary information for all available tickers.

        Latest price snapshot, best bid/ask price, trading volume in last 24 hours.

        Args:
            instrument_type: Instrument type ("SPOT", "SWAP", "FUTURES", "OPTION")
            underlying: Underlying asset, e.g. "BTC-USDT"; only for FUTURES/SWAP/OPTION
        """
        q = QueryParams(instType=instrument_type, uly=underlying)
        return self.get("/api/v5/market/tickers", query_params=q)

    def get_ticker(self, instrument_id: Optional[str] = None) -> Dict:
        """Get summary information for a specific ticker.

        Latest price snapshot, best bid/ask price, trading volume in last 24 hours.

        Args:
            instrument_id: Instrument ID, e.g. "BTC-USDT-SWAP"
        """
        q = QueryParams(instId=instrument_id)
        return self.get("/api/v5/market/ticker", query_params=q)

    def get_index_tickers(
        self, quote_currency: Optional[str] = None, instrument_id: Optional[str] = None
    ):
        """Retrieve index tickers.

        Args:
            quote_currency: Quote currency Currently only an index with USD/USDT/BTC
            instrument_id: Instrument ID, e.g. "BTC-USDT"
        """
        if quote_currency is None and instrument_id is None:
            raise TypeError("You must define one of quote_currency or instrument_id")
        q = QueryParams(quoteCcy=quote_currency, instId=instrument_id)
        return self.get("/api/v5/market/index-tickers", query_params=q)

    def get_order_book(self, instrument_id: Optional[str] = None, book_depth: int = 1):
        """Retrieve a instrument's order book.

        Args:
            instrument_id: Instrument ID, e.g. "BTC-USDT"
            book_depth: Order book depth per side. Maximum 400, e.g. 400 bids + 400 asks
        """
        q = QueryParams(instId=instrument_id, sz=book_depth)
        return self.get("/api/v5/market/books", query_params=q)

    def get_candlesticks(
        self,
        instrument_id: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        candle_size: Optional[str] = None,
        limit: Optional[str] = None,
    ) -> Dict:
        """Retrieve the candlestick charts.

        This endpoint can retrieve the latest 1,440 data entries. Charts are
        returned in groups based on the requested bar.

        Args:
            instrument_id: Instrument ID, e.g. "BTC-USDT"
            after: Pagination of data to return records earlier than the requested ts
            before: Pagination of data to return records newer than the requested ts
            candle_size: Bar size, the default is "1m" e.g. "1m" "1H" "1D" "1W" "3M"
            limit: Number of results per request. Maximum 100; Default 100.
        """
        q = QueryParams(
            instId=instrument_id,
            before=before,
            after=after,
            bar=candle_size,
            limit=limit,
        )
        return self.get("/api/v5/market/candles", query_params=q)

    def get_candlesticks_history(
        self,
        instrument_id: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        candle_size: Optional[str] = None,
        limit: Optional[str] = None,
    ):
        """Retrieve history candlestick charts from recent years.

        Args:
            instrument_id: Instrument ID, e.g. "BTC-USDT"
            after: Pagination of data to return records earlier than the requested ts
            before: Pagination of data to return records newer than the requested ts
            candle_size: Bar size, the default is "1m" e.g. "1m" "1H" "1D" "1W" "3M"
            limit: Number of results per request. Maximum 100; Default 100.
        """
        q = QueryParams(
            instId=instrument_id,
            before=before,
            after=after,
            bar=candle_size,
            limit=limit,
        )
        return self.get("/api/v5/market/history-candles", query_params=q)

    def get_index_candlesticks(
        self,
        instrument_id: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        candle_size: Optional[str] = None,
        limit: Optional[str] = None,
    ):
        """Retrieve the candlestick charts of the index.

        This endpoint can retrieve the latest 1,440 data entries. Charts are
        returned in groups based on the requested bar.

        Args:
            instrument_id: Instrument ID, e.g. "BTC-USDT"
            after: Pagination of data to return records earlier than the requested ts
            before: Pagination of data to return records newer than the requested ts
            candle_size: Bar size, the default is "1m" e.g. "1m" "1H" "1D" "1W" "3M"
            limit: Number of results per request. Maximum 100; Default 100.
        """
        q = QueryParams(
            instId=instrument_id,
            before=before,
            after=after,
            bar=candle_size,
            limit=limit,
        )
        return self.get("/api/v5/market/index-candles", query_params=q)

    def get_mark_price_candlesticks(
        self,
        instrument_id: Optional[str] = None,
        after: Optional[str] = None,
        before: Optional[str] = None,
        candle_size: Optional[str] = None,
        limit: Optional[str] = None,
    ):
        """Retrieve the candlestick charts of mark price.

        This endpoint can retrieve the latest 1,440 data entries. Charts are
        returned in groups based on the requested bar.

        Args:
            instrument_id: Instrument ID, e.g. "BTC-USDT"
            after: Pagination of data to return records earlier than the requested ts
            before: Pagination of data to return records newer than the requested ts
            candle_size: Bar size, the default is "1m" e.g. "1m" "1H" "1D" "1W" "3M"
            limit: Number of results per request. Maximum 100; Default 100.
        """
        q = QueryParams(
            instId=instrument_id,
            before=before,
            after=after,
            bar=candle_size,
            limit=limit,
        )
        return self.get("/api/v5/market/mark-price-candles", query_params=q)

    def get_trades(
        self, instrument_id: Optional[str] = None, limit: Optional[str] = None
    ):
        """Retrieve the recent transactions of an instrument.

        Args:
            instrument_id: Instrument ID, e.g. "BTC-USDT"
            limit: Number of results per request. The maximum is 100; The default is 100
        """
        q = QueryParams(instId=instrument_id, limit=limit)
        return self.get("/api/v5/market/trades", query_params=q)

    def get_total_volume(self):
        """The 24-hour trading volume of the platform.

        The 24-hour trading volume is calculated on a rolling basis, using USD
        as the pricing unit.
        """
        return self.get("/api/v5/market/platform-24-volume")

    def get_oracle(self):
        """Cryptographically signed prices available to be posted on-chain

        Using the Open Oracle standard.
        """
        return self.get("/api/v5/market/oracle")
