"""
This script is used to initialize the database for the first time by creating all necessary tables.
"""

from orion.models import BaseModel
from orion.server import create_app


def db_init():
    """
    Create an Orion application instance and create all tables defined by its models.
    """
    app = create_app()
    BaseModel.metadata.create_all(bind=app.ctx.db.engine)

    print 'Database initialized successfully.'


if __name__ == '__main__':
    db_init()
