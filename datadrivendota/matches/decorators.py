from functools import wraps


def mapping_construct(dct):
    def decorating(func):
        dct[func.__name__] = func

        @wraps(func)
        def wrapper(*arg, **kwargs):
            return func(*arg, **kwargs)
        return wrapper
    return decorating
