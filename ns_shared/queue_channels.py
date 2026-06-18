import threading
import queue
import logging

logger = logging.Logger(__name__)


class QueueChannels:
    def __init__(self):
        self.kill_flag = threading.Event()
        self.block_detection_data = queue.Queue(1)
