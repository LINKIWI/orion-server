from unittest import TestCase

import requests
import mock

from orion.clients.geocode import ReverseGeocodingClient


class ReverseGeocodingClientTest(TestCase):
    def setUp(self):
        self.auth_client = ReverseGeocodingClient('token')
        self.unauth_client = ReverseGeocodingClient()

    @mock.patch.object(requests, 'get', return_value=mock.MagicMock(
        status_code=200,
        json=lambda: {'features': [{'place_name': 'address'}]},
    ))
    def test_reverse_geocode_valid(self, mock_request):
        result = self.auth_client.reverse_geocode('lat', 'lon')

        mock_request.assert_called_with(
            url='https://api.mapbox.com/geocoding/v5/mapbox.places/lon,lat.json'
                '?access_token=token&types=address',
        )
        self.assertEqual(result, {'place_name': 'address'})

    @mock.patch.object(requests, 'get', return_value=mock.MagicMock(
        status_code=200,
        json=lambda: {'features': []},
    ))
    def test_reverse_geocode_no_results(self, mock_request):
        result = self.auth_client.reverse_geocode('lat', 'lon')

        mock_request.assert_called_with(
            url='https://api.mapbox.com/geocoding/v5/mapbox.places/lon,lat.json'
                '?access_token=token&types=address',
        )
        self.assertIsNone(result)

    @mock.patch.object(requests, 'get')
    def test_reverse_geocode_no_access_token(self, mock_request):
        result = self.unauth_client.reverse_geocode('lat', 'lon')

        self.assertFalse(mock_request.called)
        self.assertIsNone(result)

    @mock.patch.object(requests, 'get', return_value=mock.MagicMock(status_code=401))
    def test_reverse_geocode_api_failure(self, mock_request):
        result = self.auth_client.reverse_geocode('lat', 'lon')

        mock_request.assert_called_with(
            url='https://api.mapbox.com/geocoding/v5/mapbox.places/lon,lat.json'
                '?access_token=token&types=address',
        )
        self.assertIsNone(result)
