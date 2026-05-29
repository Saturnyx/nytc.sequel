import threading


class QueueChannels:
    def __init__(self):
        self.kill_flag = threading.Event()
