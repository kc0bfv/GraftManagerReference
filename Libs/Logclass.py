import logging

class Logclass(object):
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    def info(self, text):
        self.logger.info("{}: {}".format(self, text))
    
def log_function_call(func):
    def wrapper(self, *args, **kwargs):
        self.info(
                "{}: args {}, kwargs {}".format(func.__name__, args, kwargs))
        return func(self, *args, **kwargs)
    return wrapper

def log_function_call_and_completion(func):
    def wrapper(self, *args, **kwargs):
        self.info(
                "{}: args {}, kwargs {}".format(func.__name__, args, kwargs))
        retval = func(self, *args, **kwargs)
        self.info("{}: complete".format(func.__name__))
        return retval
    return wrapper
