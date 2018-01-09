import time
from orion.models.location import Location


def location_factory(
    timestamp=int(time.time()),
    user='user',
    device='device',
    latitude=1.0,
    longitude=2.0,
    accuracy=10,
    battery=100,
    trigger='u',
    connection='m',
    tracker_id='tr',
    address='address',
):
    """
    Factory function for generating a Location instance with mock data.

    :return: An instance of models.Location with the supplied mock data.
    """
    return Location(
        timestamp=timestamp,
        user=user,
        device=device,
        latitude=latitude,
        longitude=longitude,
        accuracy=accuracy,
        battery=battery,
        trigger=trigger,
        connection=connection,
        tracker_id=tracker_id,
        address=address,
    )
