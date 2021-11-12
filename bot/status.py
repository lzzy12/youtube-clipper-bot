from typing import Optional


class ClipStatus:
    uuid: str
    status: str
    progress: float
    name: str

    def __init__(self, uuid: str, status: str, progress: float, name: str, task=None):
        self.uuid = uuid
        self.status = status
        self.progress = progress
        self.name = name
        self.task = task
