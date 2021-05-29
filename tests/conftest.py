# conftest.py
# Copyright (C) 2021 Ben Tilley <targansaikhan@gmail.com>
#
# Distributed under terms of the MIT license.

import pytest
from client import OkexClient


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [
            ("ok-access-key", None),
            ("ok-access-passphrase", None),
            ("ok-access-sign", None),
            ("ok-access-timestamp", None),
        ],
    }


@pytest.fixture
def client():
    return OkexClient()
