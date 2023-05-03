"""Stream type classes for tap-openexchangerates."""

from __future__ import annotations

from singer_sdk import typing as th  # JSON Schema typing helpers
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import (
    BaseAPIPaginator,
    JSONPathPaginator,
    SimpleHeaderPaginator,
)

from tap_openexchangerates.client import openexchangeratesStream

import copy
from datetime import timedelta, date
from typing import Any, Iterable
from requests import Response

import requests


class HistoricalStreamPaginator(JSONPathPaginator):
    def get_next(self, response: Response) -> str | None:
        """Get the next page token.

        Args:
            response: API response object.

        Returns:
            The next page token.
        """
        if self._jsonpath:
            all_matches = extract_jsonpath(
                self._jsonpath, response.json()
            )
            first_match = next(iter(all_matches), None)

            date_parsed = date.fromtimestamp(first_match)
            next_day = date_parsed + timedelta(days=1)

            # Per API spec, we cannot call historical data for the current day
            if next_day >= date.today():
                next_page_token = None
            else:
                next_page_token = str(next_day)
        else:
            next_page_token = None
        return next_page_token


class HistoricalStream(openexchangeratesStream):
    """Historical stream based on the openexchangerates API.
    https://docs.openexchangerates.org/reference/historical-json"""

    replication_key = "date"  # Enable incremental sync based on the 'date' field
    is_sorted = True  # Records are monotonically increasing based on 'date'

    next_page_token_jsonpath = "$.timestamp"  # Or override `get_next_page_token`.

    name = "historical"
    path = "/historical/"
    primary_keys = ["date", "base", "symbol"]
    schema = th.PropertiesList(
        th.Property("date", th.DateType),
        th.Property("base", th.StringType),
        th.Property("symbol", th.StringType),
        th.Property("rate", th.NumberType),
    ).to_dict()

    def get_url(self,
                context: dict | None,
                next_page_token: str | None) -> str:
        """Get stream entity URL.

        Overriding this method to perform dynamic URL generation as the date is part
        of the URL and not a query parameter.

        Args:
            context: Stream partition or context dictionary.

        Returns:
            A URL, optionally targeted to a specific partition or context.
        """
        if not next_page_token:
            starting_date = self.get_starting_replication_key_value(context)
            if not starting_date:
                next_page_token = str(self.config["start_date"])
            else:
                next_page_token = starting_date

        url = "".join([self.url_base, self.path, next_page_token or '', ".json"])
        vals = copy.copy(dict(self.config))
        vals.update(context or {})
        for k, v in vals.items():
            search_text = "".join(["{", k, "}"])
            if search_text in url:
                url = url.replace(search_text, self._url_encode(v))
        return url

    def get_new_paginator(self) -> BaseAPIPaginator:
        """Get a fresh paginator for this API endpoint.

        Returns:
            A paginator instance.
        """

        if self.next_page_token_jsonpath:
            return HistoricalStreamPaginator(self.next_page_token_jsonpath)

        return SimpleHeaderPaginator("X-Next-Page")

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Return a dictionary of values to be used in URL parameterization.

        Args:
            context: The stream context.
            next_page_token: The next page index or value.

        Returns:
            A dictionary of URL query parameters.
        """
        params: dict = {}

        if "base" in self.config:
            params["base"] = self.config.get("base")
        if "symbols" in self.config:
            params["symbols"] = self.config.get("symbols")

        return params

    def prepare_request(
        self,
        context: dict | None,
        next_page_token: openexchangeratesStream._TToken | None,
    ) -> requests.PreparedRequest:
        """Prepare a request object for this stream.

        We override the get_url to perform dynamic URL generation as the date is part
        of the URL and not a query parameter.

        Args:
            context: Stream partition or context dictionary.
            next_page_token: Token, page number or any request argument to request the
                next page of data.

        Returns:
            Build a request with the stream's URL, path, query parameters,
            HTTP headers and authenticator.
        """
        http_method = self.rest_method
        url: str = self.get_url(context, next_page_token)
        params: dict = self.get_url_params(context, next_page_token)
        request_data = self.prepare_request_payload(context, next_page_token)
        headers = self.http_headers

        return self.build_prepared_request(
            method=http_method,
            url=url,
            params=params,
            headers=headers,
            json=request_data,
        )

    def parse_response(self, response: requests.Response) -> Iterable[dict]:
        """Parse the response and return an iterator of result records.

        Args:
            response: The HTTP ``requests.Response`` object.

        Yields:
            Each record from the source.
        """

        resp = response.json()
        base = resp["base"]
        parsed_date = date.fromtimestamp(resp["timestamp"])
        row = {}
        row.update({"date": parsed_date.isoformat()})
        row.update({"base": base})

        for symbol, rate in resp["rates"].items():
            row.update({"symbol": symbol})
            row.update({"rate": rate})
            yield row
