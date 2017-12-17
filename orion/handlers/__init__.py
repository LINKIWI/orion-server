from orion.handlers.publish_handler import PublishHandler
from orion.handlers.query_handler import QueryHandler
from orion.handlers.users_handler import UsersHandler


# List of all handler classes to add to the server's route/endpoint definitions.
handler_classes = [
    PublishHandler,
    QueryHandler,
    UsersHandler,
]
