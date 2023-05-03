"""Tests standard tap features using the built-in SDK tests library."""

from __future__ import annotations

import responses
import pytest
import re
from tap_openexchangerates.tap import Tapopenexchangerates
from singer_sdk.testing import get_standard_tap_tests
from .test_config import get_custom_tap_tests

SAMPLE_CONFIG = {
    "start_date": "2023-04-23",
    "app_id": "1234567890",
    "base": "USD",
    "user_agent": "tap-openexchangerates/0.0.1",
    "symbols": ["ZWL"]
}


@pytest.fixture()
def historical_response():
    """Return a sample response for the historical stream."""
    return {"disclaimer": "",
            "license": "",
            "timestamp": 1682207982,
            "base": "USD",
            "rates": {"ZWL": 322.12}}


@responses.activate
def test_standard_tap_tests(historical_response: dict):
    """Run standard tap tests from the SDK."""
    responses.add_passthru(re.compile("https://raw.githubusercontent.com/\\w+"))

    responses.add(
        responses.GET,
        re.compile("https://openexchangerates.org/api/historical.*"),
        json=historical_response,
        status=200,
    )

    tests = get_standard_tap_tests(Tapopenexchangerates, config=SAMPLE_CONFIG)
    for test in tests:
        test()


@responses.activate
def test_custom_tap_tests(historical_response: dict):
    responses.add_passthru(re.compile("https://raw.githubusercontent.com/\\w+"))
    responses.add(
        responses.GET,
        re.compile("https://openexchangerates.org/api/historical.*"),
        json=historical_response,
        status=200,
    )

    tests = get_custom_tap_tests(Tapopenexchangerates, config=SAMPLE_CONFIG)
    for test in tests:
        test()
