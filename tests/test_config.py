from singer_sdk.testing.templates import StreamTestTemplate, TapTestTemplate
import requests
import json
from mock import patch
from tap_openexchangerates.streams import HistoricalStream


class StreamConfigurationTest(StreamTestTemplate):

    name = 'stream_configuration_test'

    def test(self) -> None:
        assert self.stream.primary_keys == ['date', 'base', 'symbol']
        assert self.stream.replication_key == 'date'
        assert self.stream.replication_method == 'INCREMENTAL'
        assert self.stream.is_sorted is True
        assert self.stream.next_page_token_jsonpath == '$.timestamp'

        assert self.stream.schema == {
            'type': 'object',
            'properties': {
                'date': {'type': ['string', 'null'], 'format': 'date'},
                'base': {'type': ['string', 'null']},
                'symbol': {'type': ['string', 'null']},
                'rate': {'type': ['number', 'null']}}}

        assert self.stream.path == '/historical/'
        assert self.stream.name == 'historical'

        assert self.stream.url_base == 'https://openexchangerates.org/api'


class StreamParseResponseTest(StreamTestTemplate):

    name = 'stream_parse_response_test'

    def test(self) -> None:
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = json.loads(
                '{"disclaimer":"","license":"","timestamp":1682207982,'
                '"base":"USD","rates":{"ZWL":322.12}}')

            response = requests.get('https://openexchangerates.org/api/historical/2023-04-23.json')
            result = self.stream.parse_response(response)
            expected_keys = ['date', 'base', 'symbol', 'rate']
            for record in result:
                assert isinstance(record, dict)
                assert list(record.keys()) == expected_keys
                assert isinstance(record['date'], str)
                assert isinstance(record['base'], str)
                assert isinstance(record['symbol'], str)
                assert isinstance(record['rate'], float)


class StreamGetUrlTest(StreamTestTemplate):

    name = 'stream_get_url_test'

    def test(self) -> None:
        # Test with next page token
        context = {"foo": "bar"}
        next_page_token = "2022-01-01"
        url = self.stream.get_url(context, next_page_token)
        assert isinstance(url, str)
        assert "2022-01-01" in url
        assert ".json" in url

        # Test with starting replication key value in context
        with patch.object(HistoricalStream, 'get_starting_replication_key_value') as mock_get:
            mock_get.return_value = "2021-01-01"

            context = {"replication_key": "2021-01-01"}
            url = self.stream.get_url(context, None)
            assert isinstance(url, str)
            assert "2021-01-01" in url
            assert ".json" in url

        # Test with no starting replication key value or next page token
        url = self.stream.get_url(None, None)
        assert isinstance(url, str)
        assert "start_date" not in url
        assert ".json" in url


class TapChildStreamTest(TapTestTemplate):

    name = 'tap_child_stream_test'

    def test(self) -> None:
        streams = self.tap.discover_streams()
        assert isinstance(streams, list)
        assert len(streams) == 1
        assert isinstance(streams[0], HistoricalStream)


class TapConfigTest(TapTestTemplate):

    name = 'tap_child_stream_test'

    def test(self) -> None:
        assert self.tap.name == 'tap-openexchangerates'
        assert self.tap.config['app_id']
        assert self.tap.config['start_date'] == '2023-04-23'
        assert self.tap.config['base'] == 'USD'
        assert self.tap.config['symbols'] == ['ZWL']
        assert self.tap.config['user_agent'] == "tap-openexchangerates/0.0.1"
