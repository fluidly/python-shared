class DropMessageException(Exception):
    def __init__(self, reraise=False):
        self.reraise = reraise
