from functools import wraps


def require_params(*params):
    """
    Decorator factory that provides an abstraction over handler "run" methods to require input
    parameters in the JSON payload. Requests that fail to supply all the necessary parameters are
    rejected with an HTTP 400.

        @require_params('arg1', 'arg2')
        def run(self, *args, **kwargs):
            ...

    :param params: Varargs list of string keys to require in the JSON input payload.
    :return: A decorator to use on the handler's "run" method.
    """
    def decorator(func):
        @wraps(func)
        def wrapped_run(self, *args, **kwargs):
            missing_params = [
                required_param
                for required_param in params
                if required_param not in self.data
            ]
            if missing_params:
                return self.error(
                    data=missing_params,
                    status=400,
                    message='Required params are missing!',
                )

            return func(self, *args, **kwargs)

        return wrapped_run

    return decorator
