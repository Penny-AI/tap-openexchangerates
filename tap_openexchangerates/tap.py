"""openexchangerates tap class."""

from __future__ import annotations

from singer_sdk import Tap
from singer_sdk import typing as th  # JSON schema typing helpers

from tap_openexchangerates import streams


class Tapopenexchangerates(Tap):
    """openexchangerates tap class."""

    name = "tap-openexchangerates"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "app_id",
            th.StringType,
            required=True,
            secret=True,  # Flag config as protected.
            description="Your unique App ID",
        ),
        th.Property(
            "date",
            th.DateType,
            required=True,
            description="The requested start date in YYYY-MM-DD format",
        ),
        th.Property(
            "symbols",
            th.ArrayType(th.StringType),
            required=False,
            description="Limit results to specific currencies (comma-separated list of 3-letter codes)",
        ),
        th.Property(
            "base",
            th.StringType,
            required=False,
            description="Change base currency (3-letter code, default: USD)",
        ),
        th.Property(
            "user_agent",
            th.StringType,
            required=False,
            description="User agent to use in the request",
        ),
    ).to_dict()

    def discover_streams(self) -> list[streams.openexchangeratesStream]:
        """Return a list of discovered streams.

        Returns:
            A list of discovered streams.
        """
        return [
            streams.HistoricalStream(self)
        ]


if __name__ == "__main__":
    Tapopenexchangerates.cli()
