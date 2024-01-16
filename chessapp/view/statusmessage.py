class StatusMessage:
    def __init__(self, text: str, timeout_milliseconds: int = 2000):
        self.text = text
        self.timeout_milliseconds = timeout_milliseconds