class ISEAPIError(Exception):
    response = None
    data = {}
    code = -1
    message = "An unknown error occurred"

    def __init__(self, message=None, code=None, data={}, response=None):
        self.response = response
        if message:
            self.message = message
        if code:
            self.code = code
        if data:
            self.data = data

    def __str__(self):
        if self.code:
            return f"{self.message}"
        return self.message


# Specific exception classes
class SponsorAuthMissing(ISEAPIError):
    pass


class ObjectAlreadyExists(ISEAPIError):
    pass
