"""REST client handling, including openexchangeratesStream base class."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

import requests
from singer_sdk.authenticators import APIKeyAuthenticator
from singer_sdk.streams import RESTStream

_Auth = Callable[[requests.PreparedRequest], requests.PreparedRequest]
SCHEMAS_DIR = Path(__file__).parent / Path("./schemas")


class openexchangeratesStream(RESTStream):
    """openexchangerates stream class."""

    url_base = "https://openexchangerates.org/api"

    @property
    def authenticator(self) -> APIKeyAuthenticator:
        """Return a new authenticator object.

        Returns:
            An authenticator instance.
        """
        return APIKeyAuthenticator.create_for_stream(
            self,
            key="app_id",
            value=self.config.get("app_id", ""),
            location="params",
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        headers = {}
        if "user_agent" in self.config:
            headers["User-Agent"] = self.config.get("user_agent")

        headers["accept"] = "application/json"

        return headers
