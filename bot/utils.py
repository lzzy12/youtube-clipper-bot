import threading
import time
from bot.status import ClipStatus

class Status:
    STATUS_UPLOADING = "Uploading"
    STATUS_CLIPPING = "Clipping"
    STATUS_METADATA = "Extracting metadata"


def get_readable_file_size(size_in_bytes) -> str:
    size_units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    if size_in_bytes is None:
        return '0B'
    index = 0
    while size_in_bytes >= 1024:
        size_in_bytes /= 1024
        index += 1
    try:
        return f'{round(size_in_bytes, 2)}{size_units[index]}'
    except IndexError:
        return 'File too large'


def get_progress_bar_string(progress: float) -> str:
    PROGRESS_MAX_SIZE = 100 // 8
    PROGRESS_INCOMPLETE = ['▏', '▎', '▍', '▌', '▋', '▊', '▉']
    p = round(progress)
    cFull = p // 8
    cPart = p % 8 - 1
    p_str = '█' * cFull
    if cPart >= 0:
        p_str += PROGRESS_INCOMPLETE[cPart]
    p_str += ' ' * (PROGRESS_MAX_SIZE - cFull)
    p_str = f"[{p_str}]"
    return p_str


class SetInterval:
    def __init__(self, interval, action, args=()):
        self.interval = interval
        self.action = action
        self.stopEvent = threading.Event()
        self.args = args
        thread = threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self):
        nextTime = time.time() + self.interval
        while not self.stopEvent.wait(nextTime - time.time()):
            nextTime += self.interval
            self.action(*self.args)

    def cancel(self):
        self.stopEvent.set()


def get_readable_message(status: ClipStatus) -> str:
    msg = ""
    msg += f"<i>{status.name}</i> \n"
    msg += f"{status.status}\n"
    return msg
