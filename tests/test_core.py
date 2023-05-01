"""Tests standard tap features using the built-in SDK tests library."""

from singer_sdk.testing import get_tap_test_class
from tap_openexchangerates.tap import Tapopenexchangerates
from singer_sdk.testing.suites import TestSuite
from .test_config import (
    StreamConfigurationTest,
    StreamParseResponseTest,
    StreamGetUrlTest,
    TapChildStreamTest,
    TapConfigTest)

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

# Run standard built-in tap tests from the SDK:
TestTapopenexchangerates = get_tap_test_class(
    tap_class=Tapopenexchangerates,
    config=SAMPLE_CONFIG,
    custom_suites=[tap_stream_test_suite, tap_tap_test_suite]
)
