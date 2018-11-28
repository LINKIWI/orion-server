import functools

from flask import request

from orion.handlers.base_handler import BaseHandler
from orion.models.location import Location


def cached_reverse_geocode(func):
    """
    Decorator abstracting cache read and write semantics for the reverse geocoding method. The
    wrapper function serves the cached value if available, but otherwise calls the wrapped function
    and sets its return value in the cache.

    :param func: Reverse geocoding method to wrap. Takes three arguments: self, lat, lon.
    :return: Wrapper function with the same API.
    """
    @functools.wraps(func)
    def cache_frontend_func(self, lat, lon):
        def approx_coord(coord):
            # Reduce the precision of the coordinate for purposes of the cache key, in an effort to
            # approximately cluster coordinates within a small area to the same reverse-geocoded
            # address. This helps reduce API QPS to Mapbox, since coordinates within a few meters
            # of one another will likely resolve to the same address anyway.
            return int(round(coord / 10e-6))

        cache = self.ctx.cache.rw_client(
            namespace='reverse-geocode',
            key='feature-place-name',
            tags={'lat': approx_coord(lat), 'lon': approx_coord(lon)},
        )

        self.ctx.metrics_event.emit_event('geocode.attempt')

        # Cache hit; bypass the wrapped function and return the cached value as-is
        cached_value = cache.get()
        if cached_value is not None:
            self.ctx.metrics_event.emit_event('geocode.cache_hit')
            return cached_value

        # Cache miss; invoke the wrapped function and cache its return value if non-null
        self.ctx.metrics_event.emit_event('geocode.cache_miss')
        value = func(self, lat, lon)
        if value is not None:
            cache.set(value, ttl=24 * 60 * 60 * 1000)  # 24 hour cache TTL

        return value

    return cache_frontend_func


class PublishHandler(BaseHandler):
    """
    Add an entry to the database for every reported location. This API is compliant with the JSON
    payload shipped by the official Android OwnTracks client, the definition of which is described
    here: http://owntracks.org/booklet/tech/json/

    Note that this endpoint itself does not concern itself with authenticating requests or users.
    It is expected that this authentication occurs at the web server (Apache/nginx) level; by the
    time a request reaches this service, it is assumed that the requesting user is valid and
    permitted to access this resource.
    """

    methods = ['POST']
    path = '/api/publish'

    def run(self, *args, **kwargs):
        # Sometimes the client tries to send a reportLocation cmd. If server
        # responds with non-200, all further location updates get backed up behind it.
        # Handle with empty 200 response
        if self.data['_type'] == 'cmd' and self.data['action'] == 'reportLocation':
            return self.success(status=200)

        if self.data['_type'] != 'location':
            return self.error(status=400, message='Not a location publish.')

        if self.data.get('topic'):
            _, user, device = self.data.get('topic').split('/')
        else:
            user = request.headers.get('X-Limit-U')
            device = request.headers.get('X-Limit-D')

        lat = self.data.get('lat')
        lon = self.data.get('lon')
        address = self._extract_address(lat, lon)

        location = Location(
            timestamp=self.data.get('tst'),
            user=user,
            device=device,
            latitude=lat,
            longitude=lon,
            accuracy=self.data.get('acc'),
            battery=self.data.get('batt'),
            trigger=self.data.get('t'),
            connection=self.data.get('conn'),
            tracker_id=self.data.get('tid'),
            address=address,
        )

        with self.ctx.metrics_latency.profile('db.write_ms'):
            self.ctx.db.session.add(location)
            self.ctx.db.session.commit()

        self.ctx.stream.emit_location(location)

        self.ctx.metrics_event.emit_event('publish_location', {'user': user, 'device': device})

        return self.success(status=201)

    @cached_reverse_geocode
    def _extract_address(self, lat, lon):
        """
        Extract a reverse geocoded address from a (latitude, longitude) coordinate, fronted by a
        cache keyed by the coordinate itself.

        :param lat: Latitude of the coordinate.
        :param lon: Longitude of the coordinate.
        :return: String representation of the coordinate's address.
        """
        self.ctx.metrics_event.emit_event('geocode.api_request')
        feature = self.ctx.geocode.reverse_geocode(lat, lon)
        if not feature:
            self.ctx.metrics_event.emit_event('geocode.api_failure')
            return

        return feature.get('place_name')
