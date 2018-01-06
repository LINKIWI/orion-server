from sqlalchemy import Column
from sqlalchemy import Index
from sqlalchemy import Integer
from sqlalchemy import Numeric
from sqlalchemy import String

from orion.models import BaseModel


class Location(BaseModel):
    """
    Model representing a single location entry.
    """

    __tablename__ = 'location'
    __table_args__ = (Index('user_device_idx', 'user', 'device'),)

    location_id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(Integer)
    user = Column(String(256), index=True)
    device = Column(String(256), index=True)
    # Retain 10 decimal points for at most 3 integer places
    latitude = Column(Numeric(precision=13, scale=10, asdecimal=False))
    longitude = Column(Numeric(precision=13, scale=10, asdecimal=False))
    accuracy = Column(Integer, default=None)
    battery = Column(Integer, default=None)
    trigger = Column(String(1), default=None)
    connection = Column(String(1), default=None)
    tracker_id = Column(String(2), default=None)
    address = Column(String(256), default=None)

    def __init__(
        self,
        timestamp,
        user,
        device,
        latitude,
        longitude,
        accuracy,
        battery,
        trigger,
        connection,
        tracker_id,
        address,
    ):
        """
        Create a location report entry.

        :param timestamp: Client-reported Unix timestamp of the location.
        :param user: Associated username.
        :param device: User's device name.
        :param latitude: Latitude, as a float.
        :param longitude: Longitude, as a float.
        :param accuracy: Accuracy in meters.
        :param battery: Device's battery percentage at the time of reporting.
        :param trigger: Single-character code representing the trigger mechanism.
        :param connection: Single-character code representing the network connection type when the
                           report was created.
        :param tracker_id: Client-specified tracker ID.
        :param address: Reverse-geocoded address of this coordinate.
        """
        self.timestamp = timestamp
        self.user = user
        self.device = device
        self.latitude = latitude
        self.longitude = longitude
        self.accuracy = accuracy
        self.battery = battery
        self.trigger = trigger
        self.connection = connection
        self.tracker_id = tracker_id
        self.address = address

    def serialize(self, fields=()):
        """
        Serialize the model into a JSON payload.

        :param fields: Optional list of fields (keys) to include in the serialization. If empty or
                       otherwise falsey, all fields are included.
        :return: A JSON payload representing the location entry.
        """
        full_serialization = {
            'location_id': self.location_id,
            'timestamp': self.timestamp,
            'user': self.user,
            'device': self.device,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'accuracy': self.accuracy,
            'battery': self.battery,
            'connection': self.connection,
            'tracker_id': self.tracker_id,
            'address': self.address,
        }

        return {
            key: value
            for key, value in full_serialization.items()
            if not fields or key in fields
        }
