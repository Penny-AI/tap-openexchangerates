"""Tests standard tap features using the built-in SDK tests library."""

from singer_sdk.testing import get_tap_test_class
from tap_openexchangerates.tap import Tapopenexchangerates

SAMPLE_CONFIG = {
    "date": "2023-04-23",
    "app_id": "REPLACE_WITH_YOUR_APP_ID",
}

# Run standard built-in tap tests from the SDK:
TestTapopenexchangerates = get_tap_test_class(
    tap_class=Tapopenexchangerates,
    config=SAMPLE_CONFIG,
    custom_suites=[]
)
