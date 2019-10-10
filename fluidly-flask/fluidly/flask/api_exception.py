class APIException(Exception):
    def __init__(self, status, title, detail=None):
        self.title = title
        self.status = status
        self.detail = detail

    def to_dict(self):
        return {"title": self.title, "status": self.status, "detail": self.detail}
