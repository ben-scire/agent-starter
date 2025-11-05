"""Small FIFO buffer for short-lived conversational context."""


class ShortTermMemory:
    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self._buf: list[dict] = []

    def add(self, msg: dict) -> None:
        self._buf.append(msg)
        if len(self._buf) > self.max_messages:
            self._buf = self._buf[-self.max_messages :]

    def context(self) -> list[dict]:
        return list(self._buf)
