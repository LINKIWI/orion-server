from orion.handlers.publish_handler import PublishHandler
from orion.handlers.query_handler import QueryHandler


# List of all handler classes to add to the server's route/endpoint definitions.
handler_classes = [
    PublishHandler,
    QueryHandler,
]
