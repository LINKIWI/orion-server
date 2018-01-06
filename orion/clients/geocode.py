from functools import wraps

import googlemaps
from googlemaps.exceptions import ApiError


def graceful_api_failure(func):
    """
    Decorator for wrapping all client methods with logic to abort on API or client errors.

    :param func: Client method to wrap.
    :return: Wrapped function that returns None on failures, and proxies directly to the underlying
             function otherwise.
    """
    @wraps(func)
    def wrapped_func(self, *args, **kwargs):
        # Don't attempt to make an API call if the client is unavailable (e.g. an API key was not
        # supplied).
        if not self.gmaps_client:
            return

        try:
            return func(self, *args, **kwargs)
        except ApiError:
            return

    return wrapped_func


class ReverseGeocodingClient(object):
    """
    Client for looking up the address of a coordinate using the Google Maps API.
    """

    def __init__(self, google_api_key=None):
        """
        Create a reverse geocoding client instance.

        :param google_api_key: API key for Google Maps, with access to the Geocoding API. If an API
                               key is not supplied, all reverse geocoding calls will skip the API
                               call and return None.
        """
        if google_api_key:
            self.gmaps_client = googlemaps.Client(key=google_api_key)
        else:
            self.gmaps_client = None

    @graceful_api_failure
    def reverse_geocode(self, lat, lon):
        """
        Look up the formatted address of a coordinate expressed as a latitude and longitude.

        :param lat: Latitude of the coordinate to reverse geocode.
        :param lon: Longitude of the coordinate to reverse geocode.
        :return: String representation of the most specific address available for this coordinate;
                 None otherwise.
        """
        addresses = self.gmaps_client.reverse_geocode((lat, lon))
        if addresses:
            return addresses[0].get('formatted_address')
