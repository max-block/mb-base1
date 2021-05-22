class UserError(Exception):
    def __init__(self, message):
        super().__init__(message)


class UnregisteredDConfigError(Exception):
    def __init__(self, message):
        super().__init__(message)


class UnregisteredDValueError(Exception):
    def __init__(self, message):
        super().__init__(message)
