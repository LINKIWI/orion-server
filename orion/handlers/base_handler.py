class BaseHandler(object):
    """
    Base endpoint logic handler.
    """

    # Methods recognized by this handler.
    methods = ['GET']
    # Route recognized by this handler.
    path = None

    def __init__(self, ctx, data):
        """
        Create a handler.

        :param ctx: Application context object.
        :param data: Input JSON payload.
        """
        self.ctx = ctx
        self.data = data

    def success(self, data={}, status=200):
        """
        Return to the client with a success response.

        :param data: Optional data payload to send to the client.
        :param status: Optional HTTP status code to attach to the response.
        :return: A tuple of (response JSON, status code).
        """
        return {
            'success': True,
            'message': None,
            'data': data,
        }, status

    def error(self, data={}, status=500, message='Something went wrong.'):
        """
        Return to the client with an error response.

        :param data: Optional data payload to send to the client.
        :param status: Optional HTTP status to attach to the response.
        :param message: Optional string message describing the error.
        :return: A tuple of (response JSON, status code).
        """
        return {
            'success': False,
            'message': message,
            'data': data,
        }, status

    def run(self, *args, **kwargs):
        """
        Run the handler's core logic routine.
        """
        raise NotImplementedError('Handler logic not implemented.')
