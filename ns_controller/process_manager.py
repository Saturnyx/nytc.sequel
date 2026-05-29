import threading

from torch._C import parse_schema

import ns_perception
import ns_robot


class ProcessManager:
    def __init__(self, ugot, QueueChannels, SharedState):
        self.ugot = ugot
        self.queue_channels = QueueChannels
        self.shared_state = SharedState
        self.robot = ns_robot.Robot(ugot, QueueChannels, SharedState)

        self.threads = [threading.Thread(target=self.robot.mainloop())]

        for _ in self.threads:
            _.start()

    def mainloop(self):
        while not self.queue_channels.kill_flag.is_set():
            pass
        # now do cleanup
        for _ in self.threads:
            _.join()
        # and now he dies peacefully with all his children
