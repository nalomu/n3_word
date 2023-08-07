import schemas


class UnicornException(Exception):
    def __init__(self, message: str, data=None, code=400):
        self.response = schemas.StandardResponse(code=code, message=message, data=data)
