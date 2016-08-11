from functools import wraps


def retry_on(exc, times):
    '''
        Retry the decorated function or method, up to 'times' times
        if exception 'exc' is raised.
    '''
    assert isinstance(exc, Exception)
    assert isinstance(times, int)
    assert times >= 0
    def retry_on_decorator(method):
        @wraps(method)
        def new_method(*args, **kwargs):
            failure_count = 0
            while failure_count <= times:
                try:
                    return method(*args, **kwargs)
                except exc as e:
                    failure_count += 1
            raise e
        return new_method
    return retry_on_decorator
