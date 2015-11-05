from functools import wraps

from flask import current_app

def enqueue(task):
    ''' Decorator for Flask Resource verbs
    Decorating a verb (POST, etc.) with enqueue will call the verb, enqueue 'task' and return the response from the verb call.
    '''
    def decorator(verb):
        @wraps(verb)
        def _trigger_rq_task(*args, **kwargs):
            response = verb(*args, **kwargs)
            current_app.git_queue.enqueue(task)
            return response
        return _trigger_rq_task
    return decorator

