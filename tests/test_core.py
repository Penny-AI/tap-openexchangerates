"""Tests standard tap features using the built-in SDK tests library."""

from __future__ import annotations

import responses
from responses import _recorder
import pytest
import re
import json
from singer_sdk.testing import get_tap_test_class
from tap_openexchangerates.tap import Tapopenexchangerates
from singer_sdk.testing import get_standard_tap_tests
from singer_sdk.testing.suites import TestSuite
from .test_config import (
    StreamConfigurationTest,
    StreamParseResponseTest,
    StreamGetUrlTest,
    TapConfigTest,
    TapChildStreamTest)

SAMPLE_CONFIG = {
    "start_date": "2023-04-23",
    "app_id": "1234567890",
    "base": "USD",
    "user_agent": "tap-openexchangerates/0.0.1",
    "symbols": ["ZWL"]
}

tap_stream_test_suite = TestSuite(
    kind="tap_stream",
    tests=[
        StreamConfigurationTest,
        StreamParseResponseTest,
        StreamGetUrlTest
    ]
)

tap_tap_test_suite = TestSuite(
    kind='tap',
    tests=[
        TapConfigTest,
        TapChildStreamTest
    ]
)


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


with responses.RequestsMock() as rsps:
    rsps.add_passthru(re.compile("https://raw.githubusercontent.com/\\w+"))
    rsps.add(
        responses.GET,
        re.compile(".*"),
        json=json.dumps({"disclaimer": "",
                "license": "",
                "timestamp": 1682207982,
                "base": "USD",
                "rates": {"ZWL": 322.12}}),
        status=200
    )

    TestTapopenexchangerates = get_tap_test_class(
        tap_class=Tapopenexchangerates,
        config=SAMPLE_CONFIG,
        custom_suites=[tap_stream_test_suite, tap_tap_test_suite],
        include_tap_tests=False,
        include_stream_tests=False,
        include_stream_attribute_tests=False,
    )
