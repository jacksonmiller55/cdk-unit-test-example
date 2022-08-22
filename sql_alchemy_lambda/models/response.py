import json


class Response:
    def __init__(self, status_code: int, headers: dict, body: dict):
        self.isBase64Encoded = False
        self.statusCode = status_code
        self.headers = headers
        self.body = body

    def to_dict(self) -> dict:
        return {
            "isBase64Encoded": self.isBase64Encoded,
            "statusCode": self.statusCode,
            "headers": self.headers,
            "body": json.dumps(self.body),
        }
