from __future__ import annotations

import requests
import json
from mock import patch
from tap_openexchangerates.streams import HistoricalStream
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from singer_sdk.tap_base import Tap


def get_custom_tap_tests(
    tap_class: type[Tap],
    config: dict | None = None,
) -> list[Callable]:

    def _test_stream_configuration() -> None:
        tap = tap_class(config=config, parse_env_config=True)
        stream = tap.streams['historical']
        assert stream.primary_keys == ['date', 'base', 'symbol']
        assert stream.replication_key == 'date'
        assert stream.replication_method == 'INCREMENTAL'
        assert stream.is_sorted is True
        assert stream.next_page_token_jsonpath == '$.timestamp'

        assert stream.schema == {
            'type': 'object',
            'properties': {
                'date': {'type': ['string', 'null'], 'format': 'date'},
                'base': {'type': ['string', 'null']},
                'symbol': {'type': ['string', 'null']},
                'rate': {'type': ['number', 'null']}}}

        assert stream.path == '/historical/'
        assert stream.name == 'historical'

        assert stream.url_base == 'https://openexchangerates.org/api'

    def _test_stream_parse_response() -> None:
        tap = tap_class(config=config, parse_env_config=True)
        stream = tap.streams['historical']

        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = json.loads(
                '{"disclaimer":"","license":"","timestamp":1682207982,'
                '"base":"USD","rates":{"ZWL":322.12}}')

            response = requests.get('https://openexchangerates.org/api/historical/2023-04-23.json')
            result = stream.parse_response(response)
            expected_keys = ['date', 'base', 'symbol', 'rate']
            for record in result:
                assert isinstance(record, dict)
                assert list(record.keys()) == expected_keys
                assert isinstance(record['date'], str)
                assert isinstance(record['base'], str)
                assert isinstance(record['symbol'], str)
                assert isinstance(record['rate'], float)

    def _test_stream_get_url() -> None:
        tap = tap_class(config=config, parse_env_config=True)
        stream = tap.streams['historical']
        
        # Test with next page token
        context = {"foo": "bar"}
        next_page_token = "2022-01-01"
        url = stream.get_url(context, next_page_token)
        assert isinstance(url, str)
        assert "2022-01-01" in url
        assert ".json" in url

        # Test with starting replication key value in context
        with patch.object(HistoricalStream, 'get_starting_replication_key_value') as mock_get:
            mock_get.return_value = "2021-01-01"

            context = {"replication_key": "2021-01-01"}
            url = stream.get_url(context, None)
            assert isinstance(url, str)
            assert "2021-01-01" in url
            assert ".json" in url

        # Test with no starting replication key value or next page token
        url = stream.get_url(None, None)
        assert isinstance(url, str)
        assert "start_date" not in url
        assert ".json" in url

    def _test_tap_child_stream() -> None:
        tap: Tap = tap_class(config=config, parse_env_config=True)
        streams = tap.discover_streams()
        assert isinstance(streams, list)
        assert len(streams) == 1
        assert isinstance(streams[0], HistoricalStream)

    def _test_tap_config() -> None:
        tap: Tap = tap_class(config=config, parse_env_config=True)
        assert tap.name == 'tap-openexchangerates'
        assert tap.config['app_id']
        assert tap.config['start_date'] == '2023-04-23'
        assert tap.config['base'] == 'USD'
        assert tap.config['symbols'] == ['ZWL']
        assert tap.config['user_agent'] == "tap-openexchangerates/0.0.1"

    return [
        _test_stream_configuration,
        _test_stream_get_url,
        _test_stream_parse_response,
        _test_tap_child_stream,
        _test_tap_config
    ]
