from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import CORS
from raven.contrib.flask import Sentry

from orion.context import Context
from orion.handlers import handler_classes


def init_app(app):
    """
    Statefully initialize the Flask application. This involves creating a sever-side application
    context and adding route definitions for all endpoint handlers.

    :param app: Uninitialized Flask application instance.
    :return: Server-side application context.
    """
    ctx = Context(app)

    CORS(app, supports_credentials=True, origins=[ctx.config.get_value('frontend_url')])
    sentry_dsn = ctx.config.get_value('sentry_dsn')
    if sentry_dsn:
        Sentry(dsn=sentry_dsn).init_app(app)

    def map_handler_func(HandlerClass):
        """
        Create all necessary params for adding this route to the Flask server.

        :param HandlerClass: Handler class to prepare.
        :return: A tuple of (path, name, view_func, methods) for this handler.
        """

        def handler_wrapper(*args, **kwargs):
            # Provide an abstraction for supplying the handler with request JSON.
            data = request.get_json(force=True, silent=True) or {}
            handler = HandlerClass(ctx, data)
            resp_json, status = handler.run(*args, **kwargs)
            return jsonify(resp_json), status

        return HandlerClass.path, HandlerClass.__name__, handler_wrapper, HandlerClass.methods

    for rule, endpoint, view_func, methods in map(map_handler_func, handler_classes):
        app.add_url_rule(
            rule=rule,
            endpoint=endpoint,
            view_func=view_func,
            methods=methods,
        )

    return ctx


def create_app():
    """
    Create a fully initialized Flask application instance for this server.

    :return: The initialized Flask application instance.
    """
    app = Flask('orion')
    ctx = init_app(app)
    app.ctx = ctx
    return app
