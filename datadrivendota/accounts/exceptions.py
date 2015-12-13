class DataCapReached(BaseException):
    pass


class ValidationException(BaseException):

    def __init__(self, msg, *args, **kwargs):
        super(ValidationException, self).__init__(*args, **kwargs)
        self.strerror = msg
