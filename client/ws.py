# ws.py
# Copyright (C) 2021 Ben Tilley <targansaikhan@gmail.com>
#
# Distributed under terms of the MIT license.


import os

# import base64
# from datetime import datetime
# import hmac
# import hashlib
import json
import logging
import websockets

from typing import Optional
# from typing import Any, Awaitable, Callable, Optional

logger = logging.getLogger(__name__)


PUBLIC_CHANNELS = {
    "books",
    "candle1D",
    "estimated-price",
    "funding-rate",
    "index-candle30m",
    "index-tickers",
    "instruments",
    "mark-price",
    "mark-price-candle1D",
    "open-interest",
    "opt-summary",
    "price-limit",
    "status",
    "tickers",
    "trades",
}
PRIVATE_CHANNELS = {
    "account",
    "balance_and_position",
    "orders",
    "orders-algo",
    "positions",
}


class SocketContext:
    def __init__(self, socket, channel):
        self.socket = socket
        self.channel = channel

    async def __aenter__(self):
        return self.socket

    async def __aexit__(self, exc_type, exc, tb):
        logger.info(f"Closing conection to {self.channel}")
        await self.socket.close()
        if exc:
            logger.debug("Socket closed with exception %s", exc_type)


class OkexWebsocketsApi:
    """Websockets API client for the OKEX crypto trading platform.

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
        base_ws_url: The domain of the OKEX WebSockets API.
    """

    def __init__(
        self,
        api_key: Optional[str] = os.getenv("OKEX_API_KEY"),
        passphrase: Optional[str] = os.getenv("OKEX_PASSPHRASE"),
        secretkey: Optional[str] = os.getenv("OKEX_SECRET_KEY"),
        base_url: str = "ws.okex.com:8443/ws",
    ):
        if secretkey is None:
            logger.warning("OkexWebsocketsApi does not have a secret key")

        if api_key is None:
            raise ValueError("OkexWebsocketsApi must have an api_key")
        if passphrase is None:
            raise ValueError("OkexWebsocketsApi must have a passphrase")

        self.api_key = api_key
        self.passphrase = passphrase
        self.secretkey = secretkey
        self.base_url = base_url
        self.protocol = "wss"
        logger.info("OKEX Websocket Client Initialised")

    def connect(self, visibility: str):
        """Create a websocket connection with the OKEX server.

        Args:
            visibility: "public" or "private" - namespace of the requested channel
        """
        uri = f"{self.protocol}://{self.base_url}/v5/{visibility}"
        return websockets.connect(uri, ssl=True, ping_interval=25)  # type: ignore

    def get_channel_visibility(self, channel: str):
        """Get the visibility level of a channel.

        OKEX has "public" and "private" channels that require different levels
        of authentication.

        Args:
            channel: The channel that you want to get the visibility level for
        """
        if channel in PUBLIC_CHANNELS:
            return "public"
        elif channel in PRIVATE_CHANNELS:
            return "private"
        else:
            raise ValueError(f"Value {channel} is not a valid channel")

    async def subscribe(self, channel: str, **kwargs):
        """Set up a websocket connection to a channel.

        This method creates the initial connection with the websocket server
        and makes the handshake with the required channel.

        Args:
            channel: The channel that you want to connect to, e.g. "trades"
            kwargs: Configuration data that needs to be sent in the initial handshake
        """
        request = {"op": "subscribe", "args": [{"channel": channel, **kwargs}]}
        visibility = self.get_channel_visibility(channel)

        socket = await self.connect(visibility=visibility)
        await socket.send(json.dumps(request))
        response = json.loads(await socket.recv())

        logger.debug(f"Websocket connection response: {response}")
        if response["event"] == "subscribe":
            logger.info(f"Subscribed to channel: {channel}")
        elif response["event"] == "error":
            raise RuntimeError(
                f"Subscription to channel {channel} failed "
                f"with error \"{response['msg']}\""
            )

        return SocketContext(socket, channel)

    async def trades(self, instrument_id: str):
        """Connect to the trade channel to receive new trade messages.

        This method is an async generator, iterate over it to receive the trade
        messages being pushed to the websocket connection.

        Args:
            instrument_id: Instrument ID, e.g. "BTC-USDT"
        """
        # trades = await self.subscribe(channel="trades", instId=instrument_id)
        async with await self.subscribe(
            channel="trades", instId=instrument_id
        ) as socket:
            async for msg in socket:
                data = json.loads(msg)["data"]
                if len(data) > 1:
                    raise ValueError("More data in websocket message than expected")
                yield data[0]
