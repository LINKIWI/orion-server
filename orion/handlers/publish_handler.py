from flask import request

from orion.handlers.base_handler import BaseHandler
from orion.models.location import Location


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
        if self.data['_type'] != 'location':
            return self.error(status=400, message='Not a location publish.')

        user = request.headers.get('X-Limit-U')
        device = request.headers.get('X-Limit-D')

        location = Location(
            timestamp=self.data.get('tst'),
            user=user,
            device=device,
            latitude=self.data.get('lat'),
            longitude=self.data.get('lon'),
            accuracy=self.data.get('acc'),
            battery=self.data.get('batt'),
            trigger=self.data.get('t'),
            connection=self.data.get('conn'),
            tracker_id=self.data.get('tid'),
        )
        self.ctx.db.session.add(location)
        self.ctx.db.session.commit()

        return self.success()
