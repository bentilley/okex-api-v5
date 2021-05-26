# test_query_params.py
# Copyright (C) 2021 Ben Tilley <targansaikhan@gmail.com>
#
# Distributed under terms of the MIT license.


import pytest
from client.query_params import QueryParams


class TestQueryParams:
    def test_limit(self):
        query_params = QueryParams(limit=5)
        assert query_params["limit"] == "5"

        with pytest.raises(AssertionError, match="must be an integer"):
            QueryParams(limit="5")

        with pytest.raises(AssertionError, match="must be an integer"):
            QueryParams(limit=5.5)

        with pytest.raises(AssertionError, match="must be greater than 0"):
            QueryParams(limit=0)
