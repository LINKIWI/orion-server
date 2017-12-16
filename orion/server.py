import os

from orion.app import create_app


def main():
    """
    Run the application in a development environment.
    """
    create_app().run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5000)),
        threaded=True,
    )


if __name__ == '__main__':
    main()
